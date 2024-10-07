using Pkg
println("Installing packages...")
Pkg.add(readlines("deps.txt"))
#Pkg.add(Pkg.PackageSpec(url="https://github.com/grero/StableHashes.jl"))
#Pkg.add(url="https://github.com/grero/StableHashes.jl")
Pkg.add(Pkg.PackageSpec(path="/root/autodl-tmp/rational/optimal-planning-algorithms/model/StableHashes.jl"))
Pkg.precompile()
