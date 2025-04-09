using Serialization

function generate_unsolved_file(indices::Vector{Int})
    file_list = [
        "AwSGazpfJ1p", "My8GFVSX6F", "FFFYMCvyXkt", "9wV7Fj1yfIk", "LkJEbtwmoeJ",
        "F1Mlgj5KO6l", "2oh2eZ07INg", "CB2fIZBaN3O", "2hakOVX0gYi", "H0usFSf0Mkw",
        "IIGFrd8LpP4", "GybIvLT4pvd", "6wneZRAPgqn", "IP1EeyQ4IyN", "EaqPVDhmInR",
        "GN7VluQZ3qc", "75pC2FBdvJB", "KzgcFx9Jk7X", "1n8UTSfpRQB", "ItspCRwGKsf",
        "HKfzihcPxYE", "1Wh0OrXxrPF", "75RnmXgPpcV", "F8MlfeofaRC", "419sSUWzBYm",
        "6AkZZVHbSRj", "1ZmbVkcAaMM", "96HOu0NTLGq", "KWCOS2zn2hb", "Dz7xntFaaAX",
        "7GQrCKWqQEw", "EKReY6dggS6", "J1JhjinlRFQ", "BuDVFBx5jUw", "5ABEEdRG3iP",
        "RKupREwsTX", "vcOfOnOJHl", "7lgeRrZxRJT", "Cahmk1qC2wc", "9EZfxu5tksX",
        "1qsBhLiXZTn", "4l6guOuc6Ax", "73U6XW82HuY", "Axh3mCODRkS", "2T9ZhMZiHKp",
        "8C59Cp24e8m", "7fK64IXetRN", "9JuG5BQX3rp", "4L05OSG8slV", "LTDalc5w5Vs",
        "OVuuLBW0mE", "3pwQPvEbiSR", "HXAFlkEcgRY", "DqSYCYkw1fE", "JpS3JE0HmLB",
        "9HF3ZgTFHQv", "G93rj9nF4qo", "LjOHKf7OlB5", "1Gotz6nUYsl", "DWCYPddZyJL",
        "9PLedHL7Cau", "Fjf0eqgfnId", "DeMWohtugI6", "HogvozPpcgC", "KMP5vTuyuIU",
        "EO6prltlG4k", "LkB4cJ42nOi", "GEDCU4DamE5", "BkWAUCaqxSw", "DgU3qojIqu2",
        "KEydPnpf9PC", "dTQbTMbwUU", "3A4VgqIb5Jn", "4PCDaLUkTop", "BywUb7qk1wp",
        "5nMbZDCZ7Ty", "Bk8BAiXuf23", "1XdYIZNzdSl", "Lfk9Youlxr8", "1R6eLI1uPtN",
        "6HS5lwOPNe0", "6suRtuCU6Bj"
    ]

    # 获取 mdps/V 文件夹中的文件名
    v_files = Set(readdir("mdps/V"))  # 使用 Set 提高查找效率
    
    # 找出 file_list 中所有不在 mdps/V 中的文件
    missing_files = [file_list[i] for i in eachindex(file_list) if !(file_list[i] in v_files)]
    
    # 打印不在 V 文件夹中的文件名和序号（从 1 开始计数）
    println("Missing files and their 1-based indices:")
    for i in eachindex(file_list)
        if !(file_list[i] in v_files)
            println("File: ", file_list[i], " - Index (1-based): ", i)
        end
    end
    
    # 基于 indices 数组生成 unsolved_files
    unsolved_files = [file_list[i] for i in indices]
    println("Selected files: ", unsolved_files)
    serialize("tmp/unsolved_pseudo", unsolved_files)
    println("Serialized selected unsolved files to tmp/unsolved_pseudo")
end

indices = [12]
println("Selected indices: ", indices)

generate_unsolved_file(indices)
