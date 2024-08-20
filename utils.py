def format_time(seconds):
    """Convert seconds to a formatted string, showing only relevant time units."""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    seconds = int(seconds)

    time_str = ""

    if hours > 0:
        time_str += f"{int(hours):02}:"
    
    if minutes > 0 or hours > 0:
        time_str += f"{int(minutes):02}:"

    if hours == 0 and minutes == 0:
        if seconds < 60:
            if milliseconds > 0:
                time_str += f"{seconds}.{int(milliseconds):03} s"
            else:
                time_str += f"{seconds} s"
        else:
            time_str += f"{seconds} s"
    else:
        time_str += f"{seconds:02}"

    return time_str