from __future__ import annotations
import asyncio
import Utils
import ModuleUpdate

from CommonClient import gui_enabled, get_base_parser, server_loop

from .context import SLContext
from .commands import SLClientCommandProcessor

ModuleUpdate.update()


if __name__ == "__main__":
    Utils.init_logging("StatusLockClient", exception_logger="Client")


def main():
    async def _main(args: Utils.Namespace):
        ctx = SLContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="SL! Client, for text interfacing.")

    args, _ = parser.parse_known_args()
    colorama.init()
    asyncio.run(_main(args))
    colorama.deinit()


if __name__ == '__main__':
    main()


__all__ = ["SLClientCommandProcessor", "SLContext"]
