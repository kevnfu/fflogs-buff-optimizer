Q_MASTER_DATA = """
query MasterData ($reportCode: String!) {
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
        }
    }
}
"""

Q_FIGHTS = """
query Fights ($reportCode: String!, $encounterID: Int, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            fights (encounterID: $encounterID, fightIDs: $fightIDs) {
                id
                encounterID
                startTime
                endTime
                fightPercentage
                lastPhaseAsAbsoluteIndex
                friendlyPlayers
            }
        }
    }
}
"""

Q_EVENTS = """
query Events ($reportCode: String!, $encounterID: Int, $startTime: Float, $endTime: Float, $filter: String, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            events(limit: 10000, 
                startTime: $startTime, endTime: $endTime,
                encounterID: $encounterID,
                filterExpression: $filter,
                fightIDs: $fightIDs) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

Q_ABILITIES = """
query Abilities ($page: Int){
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    gameData {
        abilities(limit: 100, page: $page) {
            data {
                id,
                name
            },
            current_page,
            last_page,
            has_more_pages
        }
    }
}
"""

Q_AURAS = """
query Auras ($reportCode: String!, $startTime: Float, $endTime: Float, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            auras: events(limit: 10000, # hostilityType: Enemies,
                startTime: $startTime, endTime: $endTime,
                filterExpression: "inCategory('auras')=true AND type in ('applybuff','applydebuff','removebuff','removedebuff')",
                fightIDs: $fightIDs) {
                data
                nextPageTimestamp
            }
        }
    }
}
"""

Q_COMBATANT_INFO = """
query CombatantInfo ($reportCode: String!, $startTime: Float, $endTime: Float, $fightIDs: [Int]) {
    rateLimitData {
        limitPerHour
        pointsSpentThisHour
    }
    reportData {
        report(code: $reportCode) {
            info: events(limit: 10000, # hostilityType: Enemies,
                startTime: $startTime, endTime: $endTime,
                filterExpression: "type='combatantinfo'",
                fightIDs: $fightIDs) {
                data
            }
        }
    }
}
"""