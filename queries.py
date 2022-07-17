Q_REPORT = """
query Report ($reportCode: String!, $encounterID: Int) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            title
            owner {
                id
                name
            }
            startTime
            endTime
            guild {
                id
                name
                server {
                    slug
                    region {
                        slug
                    }
                }
            }
            masterData {
                bosses: actors(subType: "Boss") {
                    id
                    name
                }
                players: actors(type: "Player") {
                    id
                    name
                }
                actors {
                    id
                    gameID
                    name
                    type
                    subType
                }
                abilities {
                    gameID
                    name
                    # type
                }
            }
            fights (encounterID: $encounterID) {
                id
                encounterID
                startTime
                endTime
                fightPercentage
                lastPhaseAsAbsoluteIndex
            }
        }
    }
}
"""

Q_DEATHS = """
query Deaths {{
    reportData {{
        report(code: "{reportCode}") {{
            # filterExpression: "inCategory('deaths')=true"
            events(dataType: Deaths, limit: 10000, startTime: {startTime}, endTime: {endTime}) {{
                data
                nextPageTimestamp
            }}
        }}
    }}
}}

"""

Q_OVERKILL = """
query {{
    reportData {{
        report(code: "{reportCode}") {{
            events(dataType: DamageDone, filterExpression: "overkill > 0",
                hostilityType: Friendlies, limit: 10000, 
                startTime: {startTime}, endTime: {endTime}) {{
                data
                nextPageTimestamp
            }}
        }}
    }}
}}

"""

Q_DEATHS_OVERKILLS = """
query DeathsAndOverkills ($reportCode: String!, $startTime: Float, $endTime: Float) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            deaths: events(dataType: Deaths, limit: 10000, startTime: $startTime, endTime: $endTime) {
                data
                nextPageTimestamp
            }
            overkills: events(dataType: DamageDone, filterExpression: "overkill > 0",
                hostilityType: Friendlies, limit: 10000, 
                startTime: $startTime, endTime: $endTime) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

Q_ENCOUNTER = """
query {{
    worldData {{
        encounter(id: {encounterID}) {{
            zone {{
                name
            }}
        }}
    }}
}}
"""

Q_EVENTS = """
query Events ($reportCode: String!, $startTime: Float, $endTime: Float, $filter: String) {
    reportData {
        report(code: $reportCode) {
            events(limit: 10000, 
                startTime: $startTime, endTime: $endTime,
                filterExpression: $filter) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

Q_P5_END = """
query P5End ($reportCode: String!, $startTime: Float, $endTime: Float){
    reportData {
        report(code: $reportCode) {
            events(dataType: Casts, filterExpression: "ability.id=25539"
                hostilityType: Enemies, limit: 10000, 
                startTime: $startTime, endTime: $endTime) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

Q_TIMELINE = """
query Timeline ($reportCode: String!, $startTime: Float, $endTime: Float){
    reportData {
        report(code: $reportCode) {
            deaths: events(dataType: Deaths, hostilityType: Enemies, limit: 10000, 
                startTime: $startTime, endTime: $endTime) {
                data
                # nextPageTimestamp
            }
            targetable: events(hostilityType: Enemies, limit: 10000,
                filterExpression: "type='targetabilityupdate'",
                startTime: $startTime, endTime: $endTime) {
                data
                # nextPageTimestamp
            }
        }
    }
}
"""