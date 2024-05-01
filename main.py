from core.orchestrator import Orchestator

orchestrator = Orchestator(
    "kUUNJ5fKiUjb6TWCKHKNtRgdk4MInavtE4KI8ZoHTsAQ7UmVuzo0tj52zYsZX2jP",
    "uXqkYA5tvsKnVITgdbJLaoI2FQu9iviQxaIMkCP9JIrRrUKwnyOlXyvJP8Y3fmEz",
    "BNBUSDT",
    capital=200,
    low_bound=596-37.5,
    high_bound=596+37.5,
    bots_number=900,
)


orchestrator.create_bots()
orchestrator.run()