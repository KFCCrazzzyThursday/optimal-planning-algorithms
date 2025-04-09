using Distributed
@everywhere using Pkg
@everywhere Pkg.activate(".")
@everywhere using ProgressMeter
@everywhere include("utils.jl")
@everywhere include("mdp.jl")
@everywhere include("data.jl")

COSTS = [0:0.05:4; 100]

mkpath("mdps/withcost")
mkpath("mdps/V")


function sbatch_script(n; minutes=20, memory=5000)
    """
    #!/usr/bin/env bash
    #SBATCH --job-name=solve
    #SBATCH --output=out/%A_%a
    #SBATCH --array=1-$n
    #SBATCH --time=$minutes
    #SBATCH --mem-per-cpu=$memory
    #SBATCH --cpus-per-task=1
    #SBATCH --mail-type=end
    #SBATCH --mail-user=flc2@princeton.edu

    module load julia/1.4.1
    julia solve.jl \$SLURM_ARRAY_TASK_ID
    """
end
function write_mdps(ids)
    # 过滤掉以 "." 开头的文件（比如 .ipynb_checkpoints）
    filtered_ids = filter(i -> !startswith(i, "."), ids)
    println("Starting write_mdps with filtered ids: ", filtered_ids)

    # 反序列化基础 MDP 文件，逐步打印每个文件
    base_mdps = map(filtered_ids) do i
        file = "mdps/base/$i"
        println("Deserializing file: ", file)  # 打印文件名
        mdp = deserialize(file)
        println("Deserialized MDP: ", mdp)  # 打印反序列化结果
        mdp
    end

    # 对每个基础 MDP 和成本进行变异，并保存
    all_mdps = [mutate(m, cost=c) for m in base_mdps, c in COSTS]
    println("Mutated MDPs with costs: ", all_mdps)  # 打印所有变异后的 MDP

    # 初始化文件列表
    files = String[]
    for m in base_mdps, c in COSTS
        mc = mutate(m, cost=c)
        f = "mdps/withcost/$(id(mc))"
        println("Serializing mutated MDP with cost ", c, " to file: ", f)  # 打印文件名
        serialize(f, mc)
        push!(files, f)
    end

    # 过滤出未解决的 MDP 文件
    unsolved = filter(files) do f
        unsolved_check = !isfile(replace(f, "withcost" => "V"))
        println("Checking if file ", f, " is unsolved: ", unsolved_check)  # 打印是否未解决
        unsolved_check
    end

    # 提取文件名并打印未解决的文件
    unsolved = [string(split(f, "/")[end]) for f in unsolved]
    println("Unsolved files: ", unsolved)  # 打印未解决文件列表

    # 序列化未解决文件列表
    serialize("tmp/unsolved", unsolved)
    println("Serialized unsolved files to tmp/unsolved")

    unsolved  # 返回未解决的文件名列表
end


# function write_mdps(ids)
#     base_mdps = map(ids) do i
#         #deserialize("mdps/base/$i")base_mdps = map(ids) do i
#         file = "mdps/base/AwSGazpfJ1p"
#         println("Deserializing file: ", file)  # 打印文件名
#         deserialize(file)
#     end
#     all_mdps = [mutate(m, cost=c) for m in base_mdps, c in COSTS]
    
#     files = String[]
#     for m in base_mdps, c in COSTS
#         mc = mutate(m, cost=c)
#         f = "mdps/withcost/$(id(mc))"
#         serialize(f, mc)
#         push!(files, f)
#     end
#     unsolved = filter(files) do f
#         !isfile(replace(f, "withcost" => "V"))
#     end

#     unsolved = [string(split(f, "/")[end]) for f in unsolved]
#     serialize("tmp/unsolved", unsolved)
#     unsolved
# end

write_mdps() = write_mdps(readdir("mdps/base"))

@everywhere function solve_mdp(i::String)
    #println("Process: ",getpid())
    if getpid() % 4 == 0
        println("Process with PID divisible by 4 detected. Delaying for 5 hours.")
        sleep(5 * 60 * 60)  # 延迟30分钟
    end

    m = deserialize("mdps/withcost/$i")
    if isfile("mdps/V/$i")
        println("MDP $i has already been solved.")
        return
    end

    V = ValueFunction(m)
    println("Begin solving MDP $i:  cost = $(m.cost),  hasher = $(V.hasher)"); flush(stdout)
    @time v = V(initial_belief(m))
    println("Value of initial state is ", v)
    serialize("mdps/V/$i", V)
    V = nothing
    GC.gc()
end

@everywhere do_job(id::String) = solve_mdp(id)
@everywhere do_job(idx::Int) = solve_mdp(deserialize("tmp/unsolved")[idx])
do_job(jobs) = pmap(solve_mdp, deserialize("tmp/unsolved")[jobs])

function solve_all()
    todo = write_mdps()
    println("Solving $(length(todo)) mdps.")
    do_job(eachindex(todo))
end

if basename(PROGRAM_FILE) == basename(@__FILE__)
    if ARGS[1] == "setup"
        todo = write_mdps()
        open("solve.sbatch", "w") do f
            write("solve.sbatch", sbatch_script(length(todo)))
        end

        println(length(todo), " mdps to solve with solve.sbatch")
    else  # solve an MDP (or several)
        if ARGS[1] == "all"
            solve_all()
        elseif startswith(ARGS[1], "exp")
            include("conf.jl")
            mdps = let
                all_trials = load_trials(EXPERIMENT) |> OrderedDict |> sort!
                flat_trials = flatten(values(all_trials));
                unique(getfield.(flat_trials, :m))
            end
            all_ids = map(Iterators.product(mdps, COSTS)) do (m, cost)
                id(mutate(m, cost=cost))
            end
            println("Solving $(length(all_ids)) mdps.")
            @showprogress pmap(solve_mdp, all_ids)
        else
            do_job(eval(Meta.parse(ARGS[1])))
        end
    end

end
