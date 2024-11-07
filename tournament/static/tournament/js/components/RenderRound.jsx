const RenderRound = ({roundNumber, setRoundNumber}) => {
    const [tournamentMatches, setTournamentMatches] = React.useState([]);
    const [rankedPlayers, setRankedPlayers] = React.useState([]);
    const [possibleResults, setPossibleResults] = React.useState(null);
    const [formData, setFormData] = React.useState([]);
    const [error, setError] = React.useState(false);

    React.useEffect(() => {
        const fetchPossibleResults = async () => {
            try {
                const response = await fetch("/tournament/get_possible_results");
                if (!response.ok) throw new Error("Error fetching possible results");
                const data = await response.json();
                setPossibleResults(data);
            } catch (error) {
                console.error("Error fetching options: ", error);
            }
        };

        if (possibleResults === null) fetchPossibleResults();

    }, []);

    React.useEffect(() => {
        const fetchTournamentMatches = async () => {
            try {
                const response = await fetch(`/tournament/round/${roundNumber}`);
                if (!response.ok) throw new Error(`Could not pair rivals for Round ${roundNumber}`);
                const data = await response.json();
                setTournamentMatches(data["match_data"]);
                setRankedPlayers(data["ranked_players"]);

                const initialFormData = data["match_data"].map((match) => ({
                    player1Name: match.player1.name,
                    player2Name: match.player2.name,
                    result: "AW",
                    verified: false,
                }));
                setFormData(initialFormData);

            } catch (error) {
                console.error(`There was a problem while setting matches in Round ${roundNumber}`, error);
            }
        };
        fetchTournamentMatches();
    }, [roundNumber]);



        // Function to get CSRF token from cookies
    function getCSRFToken() {
        const cookie = document.cookie.split("; ").find((c) => c.startsWith("csrftoken="));
        return cookie ? cookie.split("=")[1] : "";
    }

    const handleResultChange = (index, value) => {
        const updatedFormData = [...formData];
        updatedFormData[index].result = value;
        setFormData(updatedFormData);
    };

    const handleVerifyChange = (index) => {
        const updatedFormData = [...formData];
        updatedFormData[index].verified = !updatedFormData[index].verified;
        setFormData(updatedFormData);
    };

    const handleSubmitRound = async (e) => {
        e.preventDefault();
        setError(false);

        const allVerified = formData.every(item => item.verified && item.result);

        if (allVerified) {
            console.log("Form submitted", formData);

            try {
                await fetch("/tournament/next_round", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({roundNumber, formData})
                });
                setRoundNumber(roundNumber+1)
            } catch (error) {
                console.error("Error submitting round data", error)
            }
        } else {
            console.log("Form NOT submitted", formData);
            setError(true);
        }
    }

    return (
        <div className="page-container">
            <form onSubmit={handleSubmitRound}>
                <div className="round-container">
                    <h1>Round {roundNumber}</h1>
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
                                    <select
                                        name="result"
                                        value={formData[index] ? formData[index].result : "AW"}
                                        onChange={(e) => handleResultChange(index, e.target.value)}
                                    >
                                        {possibleResults.length > 0 &&
                                                possibleResults.map((result) => (
                                                    <option key={result.id} value={result.id}>
                                                        {result.label}
                                                    </option>
                                                ))}
                                    </select>
                                </td>
                                <td>{match.player2.name}</td>
                                <td>
                                    <input
                                        type="radio"
                                        checked={formData[index] ? formData[index].verified : false}
                                        onChange={() => handleVerifyChange(index)}
                                    />
                                </td>
                            </tr>
                            </tbody>

                        </table>
                    ))}
                    {error && <p className="error-message">Please verify all matches before submitting.</p>}
                    <button type="submit" className="submit-btn">Finish Round {roundNumber}</button>
                </div>
            </form>

            <div className="ranked-table-container">
                <table className="ranked-table">
                    <thead>
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Player</th>
                        <th scope="col">K/D</th>
                        <th scope="col">Points</th>
                    </tr>
                    </thead>
                    <tbody>
                    {rankedPlayers.map((player, index) => (
                        <tr>
                            <td scope="row">{index + 1}</td>
                            <td scope="row">{player.name}</td>
                            <td scope="row">{player.KD}</td>
                            <td scope="row">{player.points}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}