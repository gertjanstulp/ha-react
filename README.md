# React
Simplified automations for Home Assistant

## Syntax
Config
```
react:
  workflow:
    <name>:
      when: <expression>
      then: <expression>
```

Expression
```
type.entity action
[ use overwrite ]
[ use forward_action ]
[ use forward_data ]
[ if {condition} ]
[ wait until {wait_condition} ]
[ wait for {number} {seconds|minutes|hours} ]
[ wait until {time} [every {mon|tue|wed|thu|fri|sat|sun}] [use restart_mode {abort|force|rerun}] ]
[ with key=value,... ]
```
