library(tidyverse)
library(lme4)
library(broom.mixed)
library(glue)

# %% ==================== Helpers ====================

sprintf_transformer <- function(text, envir) {
  m <- regexpr(":.+$", text)
  if (m != -1) {
    format <- substring(regmatches(text, m), 2)
    regmatches(text, m) <- ""
    res <- eval(parse(text = text, keep.source = FALSE), envir)
    do.call(sprintf, list(glue("%{format}f"), res))
  } else {
    eval(parse(text = text, keep.source = FALSE), envir)
  }
}

fmt <- function(..., .envir = parent.frame()) {
  glue(..., .transformer = sprintf_transformer, .envir = .envir)
}

write_tex = function(file, tex) {
  if (!endsWith(file, ".tex")) {
    file = paste0(file, ".tex")
  }
  file = glue(file, .envir=parent.frame())
  file = str_replace(file, "[:*]", "-")
  dir.create(dirname(file), recursive=TRUE, showWarnings=FALSE)
  tex = fmt(tex, .envir=parent.frame())
  print(paste0(file, ": ", tex))
  writeLines(paste0(tex, "\\unskip"), file)
}

pval = function(p) {
  # if (p < .001) "p < .001" else glue("p = {str_sub(format(round(p, 3)), 2)}")
  if (p < .001) "p < .001" else glue("p = {str_sub(format(round(p, 3), nsmall=3), 2)}")
}

# %% ==================== Termination ====================
experiment = 1

df = read_csv(glue('tmp4r/{experiment}/hum_term.csv'))
model = glmer(is_term ~ term_reward + best_next + (term_reward + best_next|wid), data=df, family=binomial)

model %>% 
    tidy(conf.int=T) %>% 
    filter(term %in% c("best_next", "term_reward")) %>%
    rowwise() %>% group_walk(~ with(.x, 
        write_tex("stats/{experiment}/termination-{term}.tex",
          "$\\beta = {estimate:.2}$, 95\\% CI [{conf.low:.2}, {conf.high:.2}], $z = {statistic:.2}$, ${pval(p.value)}$")
    ))

df_opt = read_csv(glue('tmp4r/{experiment}/opt_term.csv'))
model_opt = glmer(is_term ~ term_reward + best_next + (term_reward+best_next|wid), 
    data=df_opt, family=binomial)

model_opt %>% 
    tidy(conf.int=T) %>% 
    filter(term %in% c("best_next", "term_reward")) %>%
    rowwise() %>% group_walk(~ with(.x, 
        write_tex("stats/{experiment}/model_termination-{term}.tex",
          "$\\beta = {estimate:.2}$, 95\\% CI [{conf.low:.2}, {conf.high:.2}]")
    ))

# %% ==================== Expansion ====================

for (experiment in 3:4) {
    df = read_csv(glue('tmp4r/{experiment}/expansion.csv'))
    model = glmer(jump ~ gain_z + (gain_z|wid), data=df, family=binomial)
    model %>% 
        tidy(conf.int=T) %>% 
        filter(term == "gain_z") %>% 
        rowwise() %>% group_walk(~ with(.x, 
            write_tex("stats/{experiment}/expansion-{term}.tex",
              "$\\beta = {estimate:.2}$, 95\\% CI [{conf.low:.2}, {conf.high:.2}], $z = {statistic:.2}$, ${pval(p.value)}$")
        ))
}