@everywhere using Pkg
@everywhere Pkg.activate(".")
@everywhere using ProgressMeter

function make_Q_table(data)
    println("Creating Q_table")
    base_mdps = unique([d.t.m for d in data])
    println("base_mdps=$(base_mdps)")
    println("COSTS=$(COSTS)")
    M = map(Iterators.product(base_mdps, COSTS)) do (m, cost)
        mutate(m, cost=cost)
    end
    grouped_ids = eachcol(id.(M))
    println("id.M=$(id.(M))")
    println("grouped_ids=$(grouped_ids)")
    res = @showprogress pmap(grouped_ids) do ids
        vs = map(load_V_nomem, ids)
        cost = vs[1].m.cost
        @assert all(v.m.cost == cost for v in vs)
        value_functions = Dict(v.m => v for v in vs)

        qs = map(data) do d
            #@show keys(value_functions)
            #@show mutate(d.t.m, cost=cost)
            V = value_functions[mutate(d.t.m, cost=cost)]
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

# function make_Q_table(data)
#     println("Creating Q_table")
#     base_mdps = unique([d.t.m for d in data])
#     M = map(Iterators.product(base_mdps, COSTS)) do (m, cost)
#         mutate(m, cost=cost)
#     end
#     grouped_ids = eachcol(id.(M))
#     res = @showprogress pmap(grouped_ids) do ids
#         vs = map(load_V_nomem, ids)
#         cost = vs[1].m.cost
#         @assert all(v.m.cost == cost for v in vs)
        
#         # 使用id或hash作为键
#         value_functions = Dict(v.m => v for v in vs)
        
#         # 打印value_functions中第一个M的id
#         first_value_function_m = first(keys(value_functions))
#         println("id of first M in value_functions: ", objectid(first_value_function_m))
        
#         qs = map(data) do d
#             mutated_m = mutate(d.t.m, cost=cost)
#             println("id of mutated M: ", objectid(mutated_m))
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

if basename(PROGRAM_FILE) == basename(@__FILE__)
    @everywhere include("base.jl")
    all_trials = load_trials(EXPERIMENT)
    println("Loaded data for ", length(all_trials), " participants")
    data = all_trials |> values |> flatten |> get_data;
    println("data=$(data)")
    serialize("$base_path/Q_table", make_Q_table(data))
    println("Wrote $base_path/Q_table")
end




