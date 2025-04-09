using Dates
using JSON

# Function to get memory usage on Windows
function get_memory_usage_windows()
    # PowerShell command to output JSON
    cmd = `powershell -Command "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory | ConvertTo-Json"`
    
    # Execute the command and capture the output
    output = read(cmd, String)
    
    # Parse the JSON output
    data = JSON.parse(output)
    
    # Extract memory values directly as integers
    total_mem_kb = data["TotalVisibleMemorySize"]
    free_mem_kb = data["FreePhysicalMemory"]
    
    # Ensure the extracted values are integers
    if !(isa(total_mem_kb, Integer) && isa(free_mem_kb, Integer))
        error("Memory values are not integers.")
    end
    
    # Calculate used memory
    used_mem_kb = total_mem_kb - free_mem_kb
    
    # Convert kilobytes to bytes
    return (total_mem_kb * 1024, used_mem_kb * 1024)
end

# Function to write logs
function write_log(file, total_mem, used_mem)
    timestamp = Dates.format(now(), "yyyy-mm-dd HH:MM:SS")
    open(file, "a") do io
        println(io, "$timestamp - Total Memory: $(total_mem / 1024 / 1024) MB, Used Memory: $(used_mem / 1024 / 1024) MB")
    end
end

# Main logic
log_file = "memory_usage.log"
println("Memory usage logging started. Logs will be saved to $log_file.")

while true
    try
        total_mem, used_mem = get_memory_usage_windows()
        write_log(log_file, total_mem, used_mem)
    catch e
        println("Error occurred: $e")
    end
    sleep(30)  # Wait for 30 seconds
end
