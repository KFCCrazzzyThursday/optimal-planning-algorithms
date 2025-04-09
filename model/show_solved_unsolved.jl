function show_solved_and_unsolved_files()
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
    v_files = Set(readdir("mdps/V"))
    v_files_2 = Set(readdir("mdps/V_2"))
    
    solved_files = Set()
    
    println("Solved files and their 1-based indices:")
    for i in eachindex(file_list)
        if file_list[i] in v_files
            push!(solved_files, file_list[i])
            println("File: ", file_list[i], " - Index (1-based): ", i)
        elseif file_list[i] in v_files_2
            push!(solved_files, file_list[i])
            println("V_2 File: ", file_list[i], " - Index (1-based): ", i)
        end
    end

    unsolved_indices = [i for i in eachindex(file_list) if !(file_list[i] in solved_files)]
    unsolved_files = [file_list[i] for i in eachindex(file_list) if !(file_list[i] in solved_files)]

    if isempty(unsolved_files)
        println("\nAll files are solved. No unsolved files remain.")
    else
        println("\nUnsolved files with their indices:")
        for i in eachindex(unsolved_files)
            println("Index (1-based): ", unsolved_indices[i], " - File: ", unsolved_files[i])
        end
        
        println("\nUnsolved files' indices (merged): ", merge_indices(unsolved_indices))
    end
end

show_solved_and_unsolved_files()
