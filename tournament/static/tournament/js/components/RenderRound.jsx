const RenderRound = ({roundNumber, setRoundNumber}) => {
    const [tournamentMatches, setTournamentMatches] = React.useState([]);
    const [possibleResults, setPossibleResults] = React.useState(null)



    React.useEffect(() => {
        const fetchPossibleResults = async () => {
            try {
                const response = await fetch("/tournament/get_possible_results");
                if (!response.ok) {
                    throw new Error("Error fetching possible results");
                }
                const data = await response.json();
                setPossibleResults(data);
            } catch (error) {
                console.error("Error fetching options: ", error);
            }
        };

        if (possibleResults === null) {  // Fetch only if not yet loaded
            fetchPossibleResults();
        }
    }, []);

    const url = `/tournament/round/${roundNumber}`
    React.useEffect(() => {
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Could not pair rivals for Round ${roundNumber}`)
                }
                return response.json();
            })
            .then(data => setTournamentMatches(data))
            .catch(error => console.error(`There was a problem while setting matches in Round ${roundNumber}`, error))
    }, [roundNumber])

    const fetchPossibleResults = async () => {
        try {
            const response = await fetch("/tournament/get_possible_results");
            const data = await response.json();

            setPossibleResults(data)
        } catch (error) {
            console.error("Error fetching options: ", error);
        }
    }



    return (
        <div className="round-container">
            {tournamentMatches.map((match, index) => (
                <table key={index} className="match-table">
                    <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">Player 1</th>
                            <th scope="col">Result</th>
                            <th scope="col">Player 2</th>
                            <th scope="col">Verify</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td scope="row">{index + 1}</td>
                            <td>{match.player1.name}</td>
                            <td>
                                <select name="result">
                                    {possibleResults.map(result => (
                                        <option key={result.id} value={result.id}>
                                            {result.label}
                                        </option>
                                    ))}
                                </select>
                            </td>
                            <td>{match.player2.name}</td>
                            <td>
                                <input type="radio" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            ))}
        </div>
    );
}