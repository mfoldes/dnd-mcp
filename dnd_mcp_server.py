#!/usr/bin/env python3
"""
D&D Knowledge Navigator - Main server entry point.

This script starts the FastMCP server that provides D&D 5e information
through the Model Context Protocol (MCP).
"""

import argparse
import logging
import sys
import traceback
import os
from typing import Any
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Import from our reorganized structure
from src.core import api_helpers
from src.core import formatters
from src.core import prompts
from src.core import tools
from src.core import resources
from src.core.cache import APICache

# Configure more detailed logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "dnd_mcp_server.log")

# Configure logging with both console and file output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

HTTP_TRANSPORTS = {"http", "streamable-http", "sse"}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the D&D Knowledge Navigator FastMCP server."
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "streamable-http", "sse"],
        default="stdio",
        help="Transport to use when running the server.",
    )
    parser.add_argument(
        "--host",
        help="Host/interface to bind when using HTTP-based transports.",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind when using HTTP-based transports.",
    )
    parser.add_argument(
        "--path",
        help="Endpoint path when using streaming HTTP transports (optional).",
    )
    return parser.parse_args(argv)


def run_app(app: FastMCP, args: argparse.Namespace) -> None:
    transport_kwargs: dict[str, Any] = {}

    if args.transport in HTTP_TRANSPORTS:
        if args.host:
            transport_kwargs["host"] = args.host
        if args.port is not None:
            transport_kwargs["port"] = args.port
        if args.path:
            transport_kwargs["path"] = args.path
        middleware_config: list[Middleware] = []
        middleware_config.append(
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=["*"],
                allow_credentials=True,
                expose_headers=["*"],
            )
        )
        transport_kwargs["middleware"] = middleware_config
        uvicorn_config = transport_kwargs.setdefault("uvicorn_config", {})
        # Uvicorn 0.38 does not yet ship a 'websockets-sansio' backend, so use the
        # standard websockets implementation to avoid KeyError.
        if isinstance(uvicorn_config, dict):
            uvicorn_config.setdefault("ws", "websockets")
    else:
        if any(value is not None for value in (args.host, args.port, args.path)):
            logger.warning(
                "Ignoring host/port/path arguments; they only apply to HTTP-based transports."
            )

    logger.info(
        "Starting FastMCP server with transport=%s host=%s port=%s path=%s",
        args.transport,
        transport_kwargs.get("host"),
        transport_kwargs.get("port"),
        transport_kwargs.get("path"),
    )

    app.run(transport=args.transport, **transport_kwargs)


def main():
    """Main entry point for the D&D Knowledge Navigator server."""
    args = parse_args(sys.argv[1:])

    # Add debug output
    print("Starting D&D Knowledge Navigator with FastMCP...", file=sys.stderr)
    print(f"Python version: {sys.version}", file=sys.stderr)
    print(f"Current directory: {os.getcwd()}", file=sys.stderr)
    print(
        f"Logs will be saved to: {os.path.abspath(log_file)}", file=sys.stderr)
    print(f"Selected transport: {args.transport}", file=sys.stderr)
    if args.transport in HTTP_TRANSPORTS:
        print(
            f"HTTP options -> host: {args.host or 'default'}, port: {args.port or 'default'}, path: {args.path or 'default'}",
            file=sys.stderr,
        )

    try:
        # Create FastMCP server
        print("Creating FastMCP server...", file=sys.stderr)
        app = FastMCP("dnd-knowledge-navigator")
        print("FastMCP server created successfully", file=sys.stderr)

        # Create shared cache with 24-hour TTL and persistence
        cache_dir = os.path.join(os.path.dirname(__file__), "cache")
        cache = APICache(ttl_hours=24, persistent=True, cache_dir=cache_dir)
        print(
            f"API cache initialized (24-hour TTL, persistent cache in {cache_dir})", file=sys.stderr)

        # Register components
        resources.register_resources(app, cache)
        tools.register_tools(app, cache)
        prompts.register_prompts(app)

        # Run the app
        print("Running FastMCP app...", file=sys.stderr)
        run_app(app, args)
        print("App run completed", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return 1


# For direct execution, we use the main() function
if __name__ == "__main__":
    sys.exit(main())
