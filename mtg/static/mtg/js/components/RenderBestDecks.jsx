const RenderBestDecks = ({setSelectedPlayer, setSelectedDeck}) => {
    const [bestDecks, setBestDecks] = React.useState([]);

    React.useEffect(() => {
        const url = "/get_best?type=deck&n=10"
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error("Error while fetching Best Decks");
                }
                return response.json();
            })
            .then(data => {
                console.log(data)
                setBestDecks(data)
            })
            .catch(error => console.error("There was a problem while fetching Best Decks", error))
    }, []);

    const handleDeckClick = (rivalId) => {
        console.log(rivalId);
        setSelectedPlayer(null)
        setSelectedDeck({id: rivalId});
    };

    const handleOwnerClick = (rivalOwnerId) => {
        console.log(rivalOwnerId);
        setSelectedDeck(null)
        setSelectedPlayer({id: rivalOwnerId})
    };

    return (
        <div>

            <div className="results-page-container">
                <h1>Hall of Fame</h1>
                <div className="results-table">
                    <table className="table">
                        <thead className="table-light, table-results">
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">Deck</th>
                            <th scope="col">Owner</th>
                            <th scope="col">Total Matches</th>
                            <th scope="col">Victories</th>
                            <th scope="col">Defeats</th>
                            <th scope="col">Draws</th>
                            <th scope="col">Win Ratio</th>
                        </tr>
                        </thead>
                        <tbody className="table-group-divider">
                        {bestDecks.map((bestDeck, index) => (
                            <tr key={bestDeck.id}>
                                <th scope="row">{index + 1}</th>
                                <td className="clickable"
                                    onClick={() => handleDeckClick(bestDeck.id)}>{bestDeck.name}</td>
                                <td className="clickable"
                                    onClick={() => handleOwnerClick(bestDeck.ownerId)}>{bestDeck.owner}</td>
                                <td>{bestDeck.total_matches}</td>
                                <td>{bestDeck.wins}</td>
                                <td>{bestDeck.losses}</td>
                                <td>{bestDeck.draws}</td>
                                <td>{bestDeck.win_ratio}%</td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    )
}
