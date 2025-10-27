# Namespace → symbols (deterministic tags). Keep short; expand later via YAML plug-ins.
ELEMENTAL = ["earth","water","air","fire","aether"]
PLANETARY = ["mercury","venus","earth","mars","jupiter","saturn","uranus","neptune","luna","sol"]
STELLAR   = ["polaris","sirius","rigel","betelgeuse","vega","arcturus","antares","aldebaran"]
GEOMETRIC = ["point","line","triangle","square","pentagon","hexagon","heptagon","octagon"]
HARMONIC  = ["unison","octave","fifth","fourth","third","sixth","minor","major"]
ANGELIC   = ["watcher","messenger","guardian","judge","healer","scribe","builder"]
ALCHEMY   = ["calcination","solution","coagulation","sublimation","mortification","distillation","projection"]
GOETIC_DENY = ["exfiltrate_net","exec_shell","write_outside_workspace"]  # sandbox denies

def normalize(ns:str, value:str)->str:
    v=value.strip().lower()
    table={"elemental":ELEMENTAL,"planetary":PLANETARY,"stellar":STELLAR,"geometric":GEOMETRIC,
           "harmonic":HARMONIC,"angelic":ANGELIC,"alchemical":ALCHEMY}
    if ns not in table: return v
    return v if v in table[ns] else ""
