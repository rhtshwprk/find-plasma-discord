import discord
from discord.ext import commands
import pandas as pd

# Client (our bot)
client = commands.Bot(command_prefix='plasma ')

# Help command


@client.command(pass_context=True)
async def h(context):
    myEmbed = discord.Embed(title="*Plasma Bot* - I am a simple bot that helps you connect with compatible blood plasma donors/recipients on your server",
                            description="*Please use the commands as formatted here.*", color=0x00ff00)
    myEmbed.set_thumbnail(
        url="https://imgur.com/beZlf0N.png")
    myEmbed.add_field(name="Find plasma donors", value="```plasma find name <space> blood_group <space> Location```This command adds you to the recipient list and fetches a list of compatible donors to your inbox.", inline=False
                      )
    myEmbed.add_field(name="Donate your blood plasma", value="```plasma donate name <space> blood_group <space> Location```This command adds you to the donor list and fetches a list of compatible recipients to your inbox.", inline=False
                      )
    await context.channel.send(embed=myEmbed)


# find "{name-0} {BloodGroup-1} {Location-2}"
@client.command(name='find')
async def find(context, *, message):
    author_id = context.message.author
    temp = message
    arr = temp.split()
    if(len(arr) != 3):
        await context.message.channel.send("Please enter the information in the correct format")
        return
    print(message)
    print(arr)
    name = arr[0]
    loc = arr[2]
    blood = arr[1].upper()
    # Checking for correct format of blood group
    if(blood == 'A+' or blood == 'A-' or blood == 'B+' or blood == 'B-' or blood == 'AB-' or blood == 'AB+' or blood == 'O-' or blood == 'O+'):
        myEmbed = discord.Embed(title=name, color=0x00ff00)
        myEmbed.add_field(name="Location", value=loc)
        myEmbed.add_field(name="Blood Group", value=blood)
        myEmbed.set_footer(text='has been added to the recipient list.')
        await context.message.channel.send(embed=myEmbed)

        # Adding the interested recipient in the needy.csv file
        df = pd.read_csv('./needy.csv', index_col=0)
        df = df.append({"user_id": (author_id), "name": (name), "location":
                        (loc), "blood_group": (blood)}, ignore_index=True)
        df.to_csv('./needy.csv')

        # Checking for compatible users in donors.csv
        df = pd.read_csv('./donors.csv', index_col=0)
        booleans = []
        for bg in df.blood_group:
            if (isCompatible(bg, blood)):
                booleans.append(True)
            else:
                booleans.append(False)
        df1 = df[booleans]
        comp = df1.values.tolist()

        # Sending an embed with the required data as a DM to the author
        if(comp):
            embed1 = discord.Embed(
                title='Compatible Donors for you', thumbnail="./logo.png")
            for i in range(len(comp)):
                embed1.add_field(
                    name=f'Name: {comp[i][1]}', value=f'> Discord ID: {comp[i][0]}\n> Blood Group: {comp[i][2]}\n> Location: {comp[i][3]}', inline=False)
            await context.message.author.send(embed=embed1)
            await context.message.author.send("Drop them a DM to ask if they can help!")
        else:
            await context.message.author.send("There is currently no one compatible with your blood group in the server. Check back later.")
    else:
        await context.message.channel.send("Please enter the information in the correct format")


# donate "{name-0} {BloodGroup-1} {Location-2}"
@client.command(name='donate')
async def donate(context, *, message):
    author_id = context.message.author
    temp = message
    arr = temp.split()
    if(len(arr) != 3):
        await context.message.channel.send("Please enter the information in the correct format")
        return
    print(message)
    print(arr)
    name = arr[0]
    loc = arr[2]
    blood = arr[1].upper()

    # Checking for correct format of blood group
    if(blood == 'A+' or blood == 'A-' or blood == 'B+' or blood == 'B-' or blood == 'AB-' or blood == 'AB+' or blood == 'O-' or blood == 'O+'):
        myEmbed = discord.Embed(title=name, color=0x00ff00)
        myEmbed.add_field(name="Location", value=loc)
        myEmbed.add_field(name="Blood Group", value=blood)
        myEmbed.set_footer(
            text='has been added to the donor list.')
        await context.message.channel.send(embed=myEmbed)

        # Adding the interested donor in the donors.csv file
        df = pd.read_csv('./donors.csv', index_col=0)
        df = df.append({"user_id": (author_id), "name": (name), "location":
                        (loc), "blood_group": (blood)}, ignore_index=True)
        df.to_csv('./donors.csv')

        # Checking the needy.csv file to find compatible recipients
        df = pd.read_csv('./needy.csv', index_col=0)
        booleans = []
        for bg in df.blood_group:
            if (isCompatible(blood, bg)):
                booleans.append(True)
            else:
                booleans.append(False)
        df1 = df[booleans]
        comp = df1.values.tolist()

        # Sending an embed with the required data as a DM to the author, if the list is non-empty
        if(comp):
            embed1 = discord.Embed(
                title='You can donate to these people', thumbnail="./logo.png")
            for i in range(len(comp)):
                embed1.add_field(
                    name=f'Name: {comp[i][1]}', value=f'> Discord ID: {comp[i][0]}\n> Blood Group: {comp[i][2]}\n> Location: {comp[i][3]}', inline=False)
            await context.message.author.send(embed=embed1)
            await context.message.author.send("Drop them a DM to let them know you can help!")
        else:
            await context.message.author.send("There is currently no one compatible with your blood group in the server. Check back later.")
    else:
        await context.message.channel.send("Please enter the information in the correct format")


# Logic to check if two blood groups are compatible or not
def isCompatible(don, rec):
    if(don == 'O-'):
        return True
    if(rec == 'AB+'):
        return True
    if(don.endswith('+') and rec.endswith('-')):
        return False
    else:
        if(don.startswith('A') and rec.startsWith('A')):
            return True
        elif(don.startswith('B') and (rec.startsWith('B') or rec.startswith('AB'))):
            return True
        elif(don.startswith('AB') and rec.startswith('AB')):
            return True
        elif(don.startswith('O')):
            return True
        else:
            return False
    return False


# Checking if the bot is online
@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game('against COVID-19'))
    print('Bot is online')

    # df1 = pd.DataFrame(
    #    {"user_id": ['xxx', 'yyy'], "name": ['Shreevardhan', 'Rohitashwa'], "blood_group": ['B+', 'AB+'], "location": ['Salt Lake', 'Kolkata']})
    # df1.to_csv('./donors.csv')

    # df2 = pd.DataFrame(
    #    {"user_id": ['www', 'zzz'], "name": ['Sonali', 'Rahul'], "blood_group": ['AB+', 'AB+'], "location": ['Salt Lake', 'Kolkata']})
    # df2.to_csv('./needy.csv')


# Run the bot on server
client.run('NzY5NjI5MjIwNjM1ODAzNjQ4.X5RzEQ.nEFE-HoBF2N8b4eMQFyxj7PwTsE')
