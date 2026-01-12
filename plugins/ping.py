import time
import psutil
import asyncio
from datetime import datetime, timedelta
from pyrogram import Client, filters
from pyrogram.types import Message
from config import ADMINS

# Bot start time for uptime calculation
BOT_START_TIME = datetime.now()


def get_readable_time(seconds: float) -> str:
    """Convert seconds to human readable format"""
    time_list = []
    time_suffix_list = ["s", "m", "h", "d"]
    
    count = int(seconds)
    
    if count == 0:
        return "0s"
    
    for i in range(4):
        if count == 0:
            break
        if i == 0:
            remainder = count % 60
            count //= 60
        elif i == 1:
            remainder = count % 60
            count //= 60
        elif i == 2:
            remainder = count % 24
            count //= 24
        else:
            remainder = count
            count = 0
        
        if remainder > 0:
            time_list.append(f"{remainder}{time_suffix_list[i]}")
    
    time_list.reverse()
    return " ".join(time_list)


def get_readable_bytes(size: int) -> str:
    """Convert bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(size) < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} PB"


@Client.on_message(filters.command("ping") & filters.user(ADMINS))
async def ping_command(client: Client, message: Message):
    """Admin-only ping command to check bot status"""
    
    # Calculate ping latency
    start_time = time.time()
    status_msg = await message.reply_text("🏓 **Pinging...**")
    ping_time = (time.time() - start_time) * 1000  # Convert to ms
    
    # Get uptime
    uptime = datetime.now() - BOT_START_TIME
    uptime_str = get_readable_time(uptime.total_seconds())
    
    # Get system stats
    try:
        cpu_usage = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get network I/O
        net_io = psutil.net_io_counters()
        bytes_sent = get_readable_bytes(net_io.bytes_sent)
        bytes_recv = get_readable_bytes(net_io.bytes_recv)
        
        # Test network speed with a simple API call
        net_start = time.time()
        try:
            me = await client.get_me()
            net_latency = (time.time() - net_start) * 1000
        except:
            net_latency = -1
        
        # Build status message
        status_text = f"""
🏓 **Pong!**

**⏱️ Response Time:** `{ping_time:.2f} ms`
**🌐 API Latency:** `{net_latency:.2f} ms`

━━━━━━━━━━━━━━━━━━━━━━

**📊 System Status:**

**⏰ Bot Uptime:** `{uptime_str}`
**🖥️ CPU Usage:** `{cpu_usage}%`
**💾 RAM:** `{memory.percent}%` ({get_readable_bytes(memory.used)}/{get_readable_bytes(memory.total)})
**💿 Disk:** `{disk.percent}%` ({get_readable_bytes(disk.used)}/{get_readable_bytes(disk.total)})

━━━━━━━━━━━━━━━━━━━━━━

**🔄 Network Stats:**

**📤 Sent:** `{bytes_sent}`
**📥 Received:** `{bytes_recv}`

━━━━━━━━━━━━━━━━━━━━━━

**🤖 Bot Info:**
**Name:** `{me.first_name}`
**Username:** @{me.username}
**Bot ID:** `{me.id}`

✅ **Status:** Bot is running smoothly!
"""
    except ImportError:
        # psutil not installed, show basic info
        try:
            me = await client.get_me()
            bot_info = f"**Name:** `{me.first_name}`\n**Username:** @{me.username}\n**Bot ID:** `{me.id}`"
        except:
            bot_info = "Unable to fetch bot info"
        
        status_text = f"""
🏓 **Pong!**

**⏱️ Response Time:** `{ping_time:.2f} ms`
**⏰ Bot Uptime:** `{uptime_str}`

**🤖 Bot Info:**
{bot_info}

⚠️ _Install psutil for detailed system stats_

✅ **Status:** Bot is running!
"""
    except Exception as e:
        status_text = f"""
🏓 **Pong!**

**⏱️ Response Time:** `{ping_time:.2f} ms`
**⏰ Bot Uptime:** `{uptime_str}`

⚠️ **Error getting system stats:** `{str(e)}`

✅ **Status:** Bot is running!
"""
    
    await status_msg.edit_text(status_text)
