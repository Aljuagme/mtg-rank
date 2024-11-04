const RenderRound1 = ({players}) => {
    console.log("round1 data: " + players)
    if (players.length < 8) {
        return <div>Not enough players to create matches.</div>;
    }

    return (
        <div>
            {players.map((player, index) =>(
                <table>
                    <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">Player1</th>
                            <th scope="col">Result</th>
                            <th scope="col">Player2</th>
                            <th scope="col">Verify</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td scope="row">{index + 1}</td>
                            <td scope="row">{player.name}</td>
                            <td scope="row">select</td>
                            <td scope="row">{player.name}</td>
                            <td scope="row">bullet button</td>
                        </tr>
                    </tbody>
                </table>


                )
            )}
        </div>
    )
}