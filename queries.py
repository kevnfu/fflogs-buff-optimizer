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