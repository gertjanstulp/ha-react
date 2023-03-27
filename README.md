# React
Simplified automations for Home Assistant

# Expose in wsl
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=8123 connectaddress=localhost connectport=8123
netsh interface portproxy show v4tov4
netsh interface portproxy delete v4tov4 listenport=8123 listenaddress=0.0.0.0
netsh interface portproxy reset