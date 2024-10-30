const RenderDeck = ({ selectedDeck, setSelectedDeck, setSelectedPlayer }) => {
    const [deck, setDeck] = React.useState(null);  // Move useState here
    const deckId = selectedDeck && selectedDeck.id;

    React.useEffect(() => {
        if (deckId) {
            const url = `/get_deck/${deckId}`;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(data => {
                    console.log(data);
                    setDeck(data);
                })
                .catch(error => console.error(`There was a problem while fetching deck with ID: ${deckId}`, error));
        }
    }, [deckId]); // Only re-run the effect if deckId changes

    if (!deck || !deck.rivals) {
        return <div>No data available for this deck.</div>;
    }

    const rivals = deck.rivals;

    const handleRivalDeckClick = (rivalId) => {
        console.log(rivalId);
        setSelectedPlayer(null)
        setSelectedDeck({ id: rivalId });
    };

    const handleRivalOwnerClick = (rivalOwnerId) => {
        console.log(rivalOwnerId);
        setSelectedDeck(null)
        setSelectedPlayer({ id: rivalOwnerId })
    };

    return (
        <div>
            <h1>{deck.category} - {deck.name}. Win Ratio: {deck.win_ratio}%</h1>
            <div className="results-page-container">
                <div className="results-table">
                    <table className="table">
                        <thead className="table-light, table-results">
                            <tr>
                                <th scope="col">#</th>
                                <th scope="col">Rival</th>
                                <th scope="col">Owner</th>
                                <th scope="col">Total Matches</th>
                                <th scope="col">Victories</th>
                                <th scope="col">Defeats</th>
                                <th scope="col">Draws</th>
                                <th scope="col">Win Ratio</th>
                            </tr>
                        </thead>
                        <tbody className="table-group-divider">
                            {rivals.length > 0 ? (
                                rivals.map((rival, index) => (
                                <tr key={rival.id}>
                                    <th scope="row">{index + 1}</th>
                                    <td className="clickable" onClick={() => handleRivalDeckClick(rival.id)}>{rival.name}</td>
                                    <td className="clickable" onClick={() => handleRivalOwnerClick(rival.owner.id)}>{rival.owner.username}</td>
                                    <td>{rival.stats.total}</td>
                                    <td>{rival.stats.wins}</td>
                                    <td>{rival.stats.losses}</td>
                                    <td>{rival.stats.draws}</td>
                                    <td>{rival.stats.win_ratio}%</td>
                                </tr>
                            ))
                        ) : (
                        <tr>
                            <td colSpan="8">No matches available for this deck</td>
                        </tr>

                        )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

