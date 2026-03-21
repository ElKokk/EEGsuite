import numpy as np
import pylsl
import threading
import time
import logging

class LSLBoard:
    """
    A BrainFlow BoardShim-compatible wrapper for LSL streams.
    This allows the EEG Viewer to use LSL streams even if the 
    underlying BrainFlow build has issues with STREAMING_BOARD.
    """
    def __init__(self, stream_id="BrainFlowEEG", master_board_id=17):
        self.stream_id = stream_id
        self.master_board_id = master_board_id
        self.inlet = None
        self.buffer = None
        self.max_buffer_size = 450000 
        self.lock = threading.Lock()
        self.streaming = False
        self.thread = None
        self.sampling_rate = 512.0
        self.num_channels = 0
        self.board_id = -2 # Simulate STREAMING_BOARD

    def prepare_session(self):
        logging.info(f"Resolving LSL stream: {self.stream_id}")
        streams = pylsl.resolve_byprop('name', self.stream_id, timeout=5.0)
        if not streams:
            # Try to resolve by type if name fails
            streams = pylsl.resolve_byprop('type', 'EEG', timeout=2.0)
            if not streams:
                raise Exception(f"Could not find LSL stream with name '{self.stream_id}' or type 'EEG'")
            logging.info(f"Found LSL stream by type 'EEG' instead of name '{self.stream_id}'")
        
        self.inlet = pylsl.StreamInlet(streams[0])
        info = self.inlet.info()
        self.sampling_rate = info.nominal_srate()
        self.num_channels = info.channel_count()
        
        # BrainFlow data format: rows are channels.
        # We'll use a large enough number of rows (100) to cover any expected channel indices.
        self.buffer = np.zeros((100, self.max_buffer_size))
        logging.info(f"LSL session prepared. Channels: {self.num_channels}, Rate: {self.sampling_rate}")

    def start_stream(self, num_samples=None, streamer_params=None):
        if not self.inlet:
            raise Exception("Session not prepared. Call prepare_session() first.")
        self.streaming = True
        self.thread = threading.Thread(target=self._pull_data)
        self.thread.daemon = True
        self.thread.start()
        logging.info("LSL streaming started")

    def _pull_data(self):
        sample_count = 0
        while self.streaming:
            try:
                chunk, timestamps = self.inlet.pull_chunk(timeout=0.1)
                if timestamps:
                    with self.lock:
                        chunk_len = len(timestamps)
                        data = np.array(chunk).T # (channels, samples)
                        
                        # Roll buffer
                        self.buffer = np.roll(self.buffer, -chunk_len, axis=1)
                        
                        # Row 0: Sequence number
                        seq = np.arange(sample_count, sample_count + chunk_len)
                        self.buffer[0, -chunk_len:] = seq
                        sample_count += chunk_len
                        
                        # Rows 1..N: Data channels
                        # Map LSL channels to rows 1..num_channels
                        for i in range(min(self.num_channels, 90)):
                            self.buffer[i+1, -chunk_len:] = data[i]
                        
                        # Last row (99): Timestamps (BrainFlow uses index 22-23 often)
                        self.buffer[99, -chunk_len:] = timestamps
                else:
                    time.sleep(0.001)
            except Exception as e:
                logging.error(f"Error pulling LSL data: {e}")
                break

    def stop_stream(self):
        self.streaming = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        logging.info("LSL streaming stopped")

    def release_session(self):
        self.stop_stream()
        self.inlet = None
        logging.info("LSL session released")

    def get_board_id(self):
        return self.board_id

    def get_current_board_data(self, num_samples):
        with self.lock:
            # Ensure num_samples is an integer for slicing
            num_samples = int(num_samples)
            # Return a copy of the last num_samples
            return self.buffer[:, -num_samples:].copy()

    def get_board_data(self):
        """BrainFlow's get_board_data() typically returns all data and clears the internal buffer."""
        with self.lock:
            data = self.buffer.copy()
            # In a real implementation we'd probably track how much was read
            # but for this viewer, get_current_board_data is primarily used.
            return data

    def is_prepared(self):
        return self.inlet is not None

    def get_sampling_rate(self, board_id=None):
        return self.sampling_rate

    @staticmethod
    def get_exg_channels(board_id):
        # Return a range that covers most possible channels (e.g., 1 to 64)
        return list(range(1, 65))
