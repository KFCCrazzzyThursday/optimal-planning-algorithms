# 引入必要的模块
using Serialization

# 检查系统剩余内存，如果小于 50GB，则暂停 2 小时
function check_memory_and_pause()
    free_mem = Sys.free_memory()  # 获取系统剩余内存，单位：字节
    threshold = 50 * 1024^3       # 50GB，转换为字节

    if free_mem < threshold
        println("系统剩余内存小于 50GB（当前为 $(free_mem / 1024^3) GB）。程序将暂停 2 小时。")
        sleep(2 * 3600)  # 暂停 2 小时（2 小时 * 3600 秒/小时）
    else
        println("系统剩余内存充足（当前为 $(free_mem / 1024^3) GB）。继续执行程序。")
    end
end

# 在脚本开始处调用函数
check_memory_and_pause()

# 下面是您的原始代码
include("mdp.jl")
        # "6wneZRAPgqn", "IP1EeyQ4IyN", "EaqPVDhmInR",
        # "GN7VluQZ3qc", "75pC2FBdvJB", "KzgcFx9Jk7X", "1n8UTSfpRQB", "ItspCRwGKsf",
        # "HKfzihcPxYE", "1Wh0OrXxrPF", "75RnmXgPpcV", "F8MlfeofaRC", "419sSUWzBYm",
        # "6AkZZVHbSRj", "1ZmbVkcAaMM", "96HOu0NTLGq", "KWCOS2zn2hb", 
        # "Dz7xntFaaAX",
        # "7GQrCKWqQEw", "EKReY6dggS6", "J1JhjinlRFQ", "BuDVFBx5jUw", "5ABEEdRG3iP",
        # "RKupREwsTX", "vcOfOnOJHl", "7lgeRrZxRJT", "Cahmk1qC2wc", "9EZfxu5tksX",
        # "1qsBhLiXZTn", "4l6guOuc6Ax", "73U6XW82HuY", "Axh3mCODRkS", "2T9ZhMZiHKp",
        # "8C59Cp24e8m", "7fK64IXetRN", "9JuG5BQX3rp", "4L05OSG8slV", "LTDalc5w5Vs",
        # "OVuuLBW0mE", 
# 定义要测试的文件 ID 列表
file_ids = [
        "3pwQPvEbiSR", "HXAFlkEcgRY", "DqSYCYkw1fE", "JpS3JE0HmLB", 
        "9HF3ZgTFHQv", "G93rj9nF4qo", "LjOHKf7OlB5", "1Gotz6nUYsl", "DWCYPddZyJL",
        "9PLedHL7Cau", "Fjf0eqgfnId", "DeMWohtugI6", "HogvozPpcgC", "KMP5vTuyuIU",
        "EO6prltlG4k", "LkB4cJ42nOi", "GEDCU4DamE5", "BkWAUCaqxSw", "DgU3qojIqu2",
        "KEydPnpf9PC", "dTQbTMbwUU", "3A4VgqIb5Jn", "4PCDaLUkTop", "BywUb7qk1wp",
        "5nMbZDCZ7Ty", "Bk8BAiXuf23", "1XdYIZNzdSl", "Lfk9Youlxr8", "1R6eLI1uPtN",
        "6HS5lwOPNe0", "6suRtuCU6Bj"
    ]

#file_ids = ["GybIvLT4pvd"]
  # 根据实际情况替换为您的文件 ID 列表

# 定义文件路径模板
file_path_template = "mdps/V/"

# 定义一个数组，用于记录有问题的文件
error_files = []

# 定义加载函数
function test_deserialize_file(file_id::String)
    filepath = file_path_template * file_id
    println("Testing deserialization of file: $filepath")
    if !isfile(filepath)
        println("File not found: $filepath")
        push!(error_files, file_id)
        return
    end
    try
        V = deserialize(filepath)
        println("Deserialization successful for file: $filepath")
        # 您可以在这里对 V 进行进一步的处理
    catch e
        try
            println("Error deserializing file $filepath: $e")
            println("Stacktrace:")
            # 安全地显示堆栈跟踪
            bt = catch_backtrace()
            if bt !== nothing
                Base.show_backtrace(stdout, bt)
            else
                println("No stacktrace available.")
            end
        catch display_error
            println("An error occurred while displaying the stacktrace: $display_error")
        end
        push!(error_files, file_id)
    end
end

# 遍历文件 ID 列表，测试每个文件的反序列化
for file_id in file_ids
    test_deserialize_file(file_id)
    println("--------------------------------------------------")
end

# 输出有问题的文件列表
if !isempty(error_files)
    println("以下文件在反序列化过程中出现错误：")
    for file_id in error_files
        println("- $file_id")
    end
else
    println("所有文件均成功反序列化。")
end
