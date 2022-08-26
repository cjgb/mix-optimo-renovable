###############################################################################
# @gilbellosta, 2022-08-26
# Not so clean code to generate graphs
###############################################################################

library(data.table)
library(lubridate)

x <- fread("results/almacenada.csv")

x$ts <- ymd_hm(x$ts)
plot(x$ts, x$almacenada / 12000, 
     type = "l", xlab = "", ylab = "GWh",
     main = "")

# divide by 12000 to transform MW5m into GWh
max_alm <- max(x$almacenada) / 12000


x <- fread("results/almacenada.csv")
x$ts <- ymd_hm(x$ts)

plot(x$ts, x$almacenada / 12000, 
     type = "l", xlab = "", ylab = "GWh",
     main = "Energía almacenada")


plot(x$ts, x$apagones / 1000, 
     type = "l", xlab = "", ylab = "GW",
     main = "Apagones (potencia no cubierta)")

plot(x$ts, x$desaprovechada / 1000, 
     type = "l", xlab = "", ylab = "GW",
     main = "Potencia desaprovechada")

# nuclear
x <- fread("/tmp/analisis-renovables-nuclear.csv")
x$ts <- ymd_hm(x$ts)

plot(x$ts, x$almacenada / 12000, 
     type = "l", xlab = "", ylab = "GWh",
     main = "Energía almacenada")


plot(x$ts, x$apagones / 1000, 
     type = "l", xlab = "", ylab = "GW",
     main = "Apagones (potencia no cubierta)")

plot(x$ts, x$desaprovechada / 1000, 
     type = "l", xlab = "", ylab = "GW",
     main = "Potencia desaprovechada")



