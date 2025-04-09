@everywhere using Pkg
@everywhere Pkg.activate(".")
@everywhere using ProgressMeter
@everywhere include("utils.jl")
# function make_Q_table(data)
#     println("Creating Q_table")
#     base_mdps = unique([d.t.m for d in data])
#     println("base_mdps=$(base_mdps)")
#     println("COSTS=$(COSTS)")
#     M = map(Iterators.product(base_mdps, COSTS)) do (m, cost)
#         mutate(m, cost=cost)
#     end
#     grouped_ids = eachcol(id.(M))
#     println("id.M=$(id.(M))")
#     println("grouped_ids=$(grouped_ids)")
#     res = @showprogress pmap(grouped_ids) do ids
#         vs = map(load_V_nomem, ids)
#         cost = vs[1].m.cost
#         @assert all(v.m.cost == cost for v in vs)
#         value_functions = Dict(v.m => v for v in vs)

#         qs = map(data) do d
#             #@show keys(value_functions)
#             #@show mutate(d.t.m, cost=cost)
#             V = value_functions[mutate(d.t.m, cost=cost)]
#             @assert haskey(V.cache, V.hasher(V.m, d.b))
#             Q(V, d.b)
#         end
#         GC.gc()
#         qs
#     end
#     all_qs = invert(res)

#     @assert length(all_qs) == length(data)
#     @assert length(all_qs[1]) == length(COSTS)
#     map(data, all_qs) do d, dqs
#         shash(d) => Dict(zip(COSTS, dqs))
#     end |> Dict
# end

# # function make_Q_table(data)
# #     println("Creating Q_table")
# #     base_mdps = unique([d.t.m for d in data])
# #     M = map(Iterators.product(base_mdps, COSTS)) do (m, cost)
# #         mutate(m, cost=cost)
# #     end
# #     grouped_ids = eachcol(id.(M))
# #     res = @showprogress pmap(grouped_ids) do ids
# #         vs = map(load_V_nomem, ids)
# #         cost = vs[1].m.cost
# #         @assert all(v.m.cost == cost for v in vs)
        
# #         # 使用id或hash作为键
# #         value_functions = Dict(v.m => v for v in vs)
        
# #         # 打印value_functions中第一个M的id
# #         first_value_function_m = first(keys(value_functions))
# #         println("id of first M in value_functions: ", objectid(first_value_function_m))
        
# #         qs = map(data) do d
# #             mutated_m = mutate(d.t.m, cost=cost)
# #             println("id of mutated M: ", objectid(mutated_m))
# #             V = value_functions[mutate(d.t.m, cost=cost)]

# #             @assert haskey(V.cache, V.hasher(V.m, d.b))
# #             Q(V, d.b)
# #         end
# #         GC.gc()
# #         qs
# #     end
# #     all_qs = invert(res)

# #     @assert length(all_qs) == length(data)
# #     @assert length(all_qs[1]) == length(COSTS)
# #     map(data, all_qs) do d, dqs
# #         shash(d) => Dict(zip(COSTS, dqs))
# #     end |> Dict
# # end

# if basename(PROGRAM_FILE) == basename(@__FILE__)
#     @everywhere include("base.jl")
#     all_trials = load_trials(EXPERIMENT)
#     println("Loaded data for ", length(all_trials), " participants")
#     data = all_trials |> values |> flatten |> get_data;
#     println("data=$(data)")
#     serialize("$base_path/Q_table", make_Q_table(data))
#     println("Wrote $base_path/Q_table")
# end


function make_Q_table(data)
    println("Creating Q_table")
    base_mdps = unique([d.t.m for d in data])
    M = map(Iterators.product(base_mdps, COSTS)) do (m, cost)
        mutate(m, cost=cost)
    end
    grouped_ids = eachcol(id.(M))
    res = @showprogress pmap(grouped_ids) do ids
        vs = map(load_V_nomem, ids)
        cost = vs[1].m.cost
        @assert all(v.m.cost == cost for v in vs)
        value_functions = Dict(v.m => v for v in vs)
        println("value_functions 中的可用键：")
        for k in keys(value_functions)
            println(k)
        end
        # qs = map(data) do d
        #     V = value_functions[mutate(d.t.m, cost=cost)]
        #     @assert haskey(V.cache, V.hasher(V.m, d.b))
        #     Q(V, d.b)
        # end

        # qs = map(data) do d
        #     key_to_find = mutate(d.t.m, cost=cost)
        #     println("尝试查找键：")
        #     println(key_to_find)

        #     if haskey(value_functions, key_to_find)
        #         V = value_functions[key_to_find]
        #     else
        #         println("键未找到。可用的键有：")
        #         for k in keys(value_functions)
        #             println(k)
        #         end
        #         error("键未在 value_functions 中找到。")
        #     end

        #     @assert haskey(V.cache, V.hasher(V.m, d.b))
        #     Q(V, d.b)
        # end

        # qs = map(data) do d
        #     key_to_find = mutate(d.t.m, cost=cost)
        #     println("尝试查找键的详细信息：")
        #     println("key_to_find 类型： ", typeof(key_to_find))
        #     for field in fieldnames(typeof(key_to_find))
        #         value = getfield(key_to_find, field)
        #         println("字段 $(field) = $(value)")
        #     end
        #     println("key_to_find 的哈希值： ", hash(key_to_find))
            
        #     found = false
        #     for k in keys(value_functions)
        #         if isequal(key_to_find, k)
        #             println("找到匹配的键。")
        #             found = true
        #             V = value_functions[k]
        #             break
        #         end
        #     end
        #     if !found
        #         println("键未找到。可用的键的详细信息：")
        #         for k in keys(value_functions)
        #             println("键 k 类型： ", typeof(k))
        #             for field in fieldnames(typeof(k))
        #                 value = getfield(k, field)
        #                 println("字段 $(field) = $(value)")
        #             end
        #             println("键 k 的哈希值： ", hash(k))
        #             println("----")
        #         end
        #         error("键未在 value_functions 中找到。")
        #     end

        #     @assert haskey(V.cache, V.hasher(V.m, d.b))
        #     Q(V, d.b)
        # end

        qs = map(data) do d
            key_to_find = mutate(d.t.m, cost=cost)
            println("尝试查找键的详细信息：")
            println("key_to_find 类型： ", typeof(key_to_find))
            # for field in fieldnames(typeof(key_to_find))
            #     value = getfield(key_to_find, field)
            #     println("字段 $(field) = $(value)")
            # end
            println("key_to_find 的哈希值： ", hash(key_to_find))
            
            V = nothing  # 在循环外部预先定义 V
            found = false
            for k in keys(value_functions)
                if isequal(key_to_find, k)
                    println("找到匹配的键。")
                    found = true
                    V = value_functions[k]
                    break
                end
            end
            if !found
                println("键未找到。可用的键的详细信息：")
                for k in keys(value_functions)
                    println("键 k 类型： ", typeof(k))
                    # for field in fieldnames(typeof(k))
                    #     value = getfield(k, field)
                    #     println("字段 $(field) = $(value)")
                    # end
                    println("键 k 的哈希值： ", hash(k))
                    println("----")
                end
                error("键未在 value_functions 中找到。")
            end

            @assert haskey(V.cache, V.hasher(V.m, d.b))
            Q(V, d.b)
        end


        GC.gc()
        qs
    end
    all_qs = invert(res)

    @assert length(all_qs) == length(data)
    @assert length(all_qs[1]) == length(COSTS)
    map(data, all_qs) do d, dqs
        shash(d) => Dict(zip(COSTS, dqs))
    end |> Dict
end

if basename(PROGRAM_FILE) == basename(@__FILE__)
    @everywhere include("base.jl")
    all_trials = load_trials(EXPERIMENT)
    println("Loaded data for ", length(all_trials), " participants")
    data = all_trials |> values |> flatten |> get_data;
    serialize("$base_path/Q_table", make_Q_table(data))
    println("Wrote $base_path/Q_table")
end