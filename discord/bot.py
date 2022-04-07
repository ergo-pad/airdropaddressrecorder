from discord.ext import commands
from discord.user import User
from discord.guild import Guild, Member, Role
from dislash import slash_commands
from dislash.interactions import *
import os
import psycopg2
import requests
from cardano_verify import verify_address

client = commands.Bot(command_prefix="!")
slash = slash_commands.SlashClient(client)

@slash.command(
    name="register",
    description="Register your address for the airdrop.",
    options=[Option("address","Your ergo wallet address",OptionType.STRING,required=True)]
    )
async def register(interaction: SlashInteraction, address: str):
    # ------------- get user & guild ------------------
    guild: Guild = interaction.guild
    member: Member = interaction.author
    user: User = interaction.author

    # ------------- get wallet info based on address ---------------
    r = requests.get(f'{os.environ.get("ERGO_NODE")}/utils/address/{address}')
    res = r.json()

    # -------------- if wallet is valid save it in the DB ------------------
    if res['isValid']:
        with psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            database=os.environ.get('POSTGRES_DB'),
            user=os.environ.get('POSTGRES_USER'),
            password=os.environ.get('POSTGRES_PASSWORD')
            ) as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO discord_wallets 
                (guild_id,user_id,user_name,guild_join_date,wallet_address) 
                VALUES 
                (%s,%s,%s,%s,%s)
                ON CONFLICT ON CONSTRAINT "discord_wallets_GUILD_ID_USER_ID"
                DO UPDATE SET
                (user_name, wallet_address, wallet_update_ts)
                = (EXCLUDED.user_name, EXCLUDED.wallet_address, CURRENT_TIMESTAMP)""",(
                    guild.id,
                    user.id,
                    member.display_name,
                    member.joined_at,
                    address
                    ))
                conn.commit()
                await interaction.reply(f"CONGRATULATIONS! 🎊 You successfully registered your Ergo Wallet address.")
    else:
        await interaction.reply("ERROR! Please re-enter a valid Ergo wallet address.")

client.run(os.environ.get("DISCORD_KEY"))