WITH leaderboard AS
(
	SELECT
	RANK() OVER w AS 'rank',
	recipient_user_id,
	SUM(amount) as `total`

	FROM
	discord_point_transactions

	WHERE
	guild_id='{}'

	GROUP BY recipient_user_id

	WINDOW w AS (ORDER BY SUM(amount) DESC)
)
SELECT
*
FROM
leaderboard
WHERE
recipient_user_id='{}'