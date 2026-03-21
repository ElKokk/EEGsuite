# eeg_viewer_main.py
"""
Main entry point for EEG Viewer Application using BrainFlow and PyQt5.
"""
import argparse
import logging
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from modules.controller import GraphController
from modules.lsl_board import LSLBoard


def main():
    BoardShim.enable_dev_board_logger()
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('--lsl-stream', type=str, help='LSL stream name or ID to read from')
    parser.add_argument('--serial-port', type=str, help='Serial port for real board')
    parser.add_argument('--board-id', type=int, default=17, help='BrainFlow board ID')
    parser.add_argument('--streamer-params', type=str, default='', help='Optional streamer parameters')
    parser.add_argument('--playback-file', type=str, default=None, help='Path to CSV file for playback mode')
    args = parser.parse_args()

    params = BrainFlowInputParams()
    if args.playback_file:
        logging.info("Playback mode activated with file: %s", args.playback_file)
        params.file = args.playback_file
        params.master_board = args.board_id
        board_id = BoardIds.PLAYBACK_FILE_BOARD.value
        board_shim = BoardShim(board_id, params)
    elif args.serial_port:
        logging.info("Serial mode activated on port: %s", args.serial_port)
        params.serial_port = args.serial_port
        board_id = args.board_id
        board_shim = BoardShim(board_id, params)
    elif args.lsl_stream:
        logging.info("LSL mode activated for stream: %s", args.lsl_stream)
        board_shim = LSLBoard(args.lsl_stream, args.board_id)
    else:
        # Default mode if nothing specified: LSL "BrainFlowEEG"
        logging.info("No specific mode requested, defaulting to LSL stream: BrainFlowEEG")
        board_shim = LSLBoard('BrainFlowEEG', args.board_id)

    try:
        board_shim.prepare_session()
        board_shim.start_stream(450000, args.streamer_params)
        #GraphController(board_shim)
        controller = GraphController(board_shim)
        controller.run()
    except Exception:
        logging.warning('Exception occurred during session', exc_info=True)
    finally:
        if board_shim.is_prepared():
            board_shim.release_session()


if __name__ == '__main__':
    main()
