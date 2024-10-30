const RenderResults = ({ setSelectedDeck, setSelectedPlayer }) => {
    const [results, setResults] = React.useState([]);
    const [bestDeck, setBestDeck] = React.useState([]);
    const [bestPlayer, setBestPlayer] = React.useState([]);
    const [showForm, setShowForm] = React.useState(false);
    const [userDecks, setUserDecks] = React.useState([]); // Options for user's decks (deck1)
    const [rivalDecks, setRivalDecks] = React.useState([]); // Options for all other decks (deck2)
    const [resultOptions, setResultOptions] = React.useState([]); // Options for match results

    React.useEffect(() => {
        const url = `/get_results`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                return response.json();
            })
            .then(data => {
                setResults(data["matches"]);
                setBestDeck(data["best_deck"]);
                setBestPlayer(data["best_player"]);
            })
            .catch(error => console.error("There was a problem while fetching results", error))
    }, []); // Empty array means this effect runs only once after the initial render

    const handleDeckClick = (deckId) => {
        setSelectedPlayer(null)
        setSelectedDeck({ id: deckId });
    };

    const handlePlayerClick = (playerId) => {
        setSelectedDeck(null)
        setSelectedPlayer({ id: playerId });
    };

    // Fetch deck options and match results on form open
    const fetchOptions = async () => {
        try {
            const response = await fetch("/get_options/result");
            const data = await response.json();
            setUserDecks(data["decks"]);
            setRivalDecks(data["rival_decks"]);
            setResultOptions(data["results_match"]);
        } catch (error) {
            console.error("Error fetching options:", error);
        }
    };

    // Function to get CSRF token from cookies
    function getCSRFToken() {
        const cookies = document.cookie.split("; ");
        for (let cookie of cookies) {
            if (cookie.startsWith("csrftoken=")) {
                return cookie.split("=")[1];
            }
        }
        return "";
    }

    const handleSubmitForm = (event) => {
        event.preventDefault();
        const formData = new FormData(event.target);

        fetch('/add_match', {
            method: 'POST',
            body: formData,
            headers: {
                "X-CSRFToken": getCSRFToken(),
            }
        }).then(response => {
            if (response.ok) {
                setShowForm(false);
                window.location.reload();
            } else {
                console.error("Failed to add match");
            }
        });
    };

    const handleAddClick = () => {
        if (showForm) {
            setShowForm(false);
        } else {
            setShowForm(true);
            fetchOptions();
        }
    }

    React.useEffect(() => {
    }, [userDecks, rivalDecks, resultOptions]);

    return (
        <div className="results-page-container">
            {/* Top tables: Best Player and Best Deck */}
            <div className="top-tables-container">
                <div className="best-player-table">
                    <table className="table">
                        <thead className="best-player-header">
                        <tr>
                            <th scope="col">Best Player</th>
                            <th scope="col">Victories</th>
                            <th scope="col">Matches Played</th>
                            <th scope="col">Win Ratio</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                            <td className="clickable"
                                onClick={() => handlePlayerClick(bestPlayer.id)}>{bestPlayer.username}</td>
                            <td>{bestPlayer.wins}</td>
                            <td>{bestPlayer.total_matches}</td>
                            <td>{bestPlayer.win_ratio}%</td>
                        </tr>
                        </tbody>
                    </table>
                </div>

                <div className="best-deck-table">
                    <table className="table">
                        <thead className="best-deck-header">
                        <tr>
                            <th scope="col">Best Deck</th>
                            <th scope="col">Owner</th>
                            <th scope="col">Victories</th>
                            <th scope="col">Matches Played</th>
                            <th scope="col">Win Ratio</th>
                        </tr>
                        </thead>
                        <tbody>
                        <tr>
                            <td className="clickable"
                                onClick={() => handleDeckClick(bestDeck.id)}>{bestDeck.name}</td>
                            <td className="clickable"
                                onClick={() => handlePlayerClick(bestDeck.ownerId)}>{bestDeck.owner}</td>
                            <td>{bestDeck.wins}</td>
                            <td>{bestDeck.total_matches}</td>
                            <td>{bestDeck.win_ratio}%</td>
                        </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Results table */}
            <div className="results-table">
                <table className="table">
                    <thead className="table-light, table-results">
                    <tr>
                        <th scope="col">#</th>
                        <th scope="col">Deck1</th>
                        <th scope="col">Result</th>
                        <th scope="col">Deck2</th>
                        <th scope="col">Datetime</th>
                    </tr>
                    </thead>
                    <tbody className="table-group-divider">
                    {results.length > 0 && results.map((match, index) => (
                        <tr key={index}>
                            <th scope="row">{index + 1}</th>
                            <td className="clickable"
                                onClick={() => handleDeckClick(match.deck1.id)}>{match.deck1.name}</td>
                            <td>{match.result}</td>
                            <td className="clickable"
                                onClick={() => handleDeckClick(match.deck2.id)}>{match.deck2.name}</td>
                            <td>{match.date_played}</td>
                        </tr>
                    ))}
                    <tr>
                        <td>
                            <button className="button-add" onClick={handleAddClick}>
                                <img
                                    onClick={() => setShowForm(!showForm)}
                                    src={showForm ? "/static/mtg/img/subtract-button.png" : "/static/mtg/img/add-button.png"}
                                    alt={showForm ? "Cancel" : "Add"}
                                />
                            </button>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>

            {/* Form to add new match */}
            {showForm && (
                <form onSubmit={handleSubmitForm} className="add-match-form">
                    <h3>Add New Match</h3>
                    <div>
                        <label>Deck 1: </label>
                        <select name="deck1">
                            {userDecks.map(deck => (
                                <option key={deck.id} value={deck.id}>{deck.name}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label>Result: </label>
                        <select name="result">
                            {resultOptions.map(result => (
                                <option key={result.id} value={result.id}>{result.label}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label>Deck 2: </label>
                        <select name="deck2">
                            {rivalDecks.map(rivalDeck => (
                                <option key={rivalDeck.id} value={rivalDeck.id}>{rivalDeck.name}</option>
                            ))}
                        </select>
                    </div>
                    <button type="submit">Submit</button>
                    <button type="button" onClick={() => setShowForm(false)}>Cancel</button>

                </form>
            )}
        </div>
    );
};
