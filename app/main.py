from app.config import settings
from app.logging_config import setup_logging
from app.server import create_mcp_server


def main() -> None:
    setup_logging()

    mcp = create_mcp_server()
    mcp.run(
        transport="http",
        host=settings.app_host,
        port=settings.app_port,
    )


if __name__ == "__main__":
    main()
