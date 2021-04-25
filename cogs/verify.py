from loguru import logger
from discord.ext import commands
import discord.utils
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


class Verification(commands.Cog):
    """
    Verify cog to verify if user is part of Saranda using their REGNO and EMAIL.
    """

    def __init__(self, client):
        self.client = client
        self.sg_client = SendGridAPIClient(os.getenv("SENDGRID_KEY"))

    
    def send_mail(self, email, code:str):
        message = Mail(
            from_email=("21f1004210@student.onlinedegree.iitm.ac.in", "Saranda House"),
            to_emails=email
        )

        message.dynamic_template_data = {
            'code': code
        }
        message.template_id = "d-d04f52087cd64e06848a3ebed47e97c0"

        try:
            response = self.sg_client.send(message)
        except Exception as e:
            logger.opt(exception=True).error("Unable to send mail", e)
            return False
        
        return True


    def check_regno(self, regno:str) -> bool:
        regno = regno.strip()
        if "," in regno:
            return False 

        email = f"{regno.upper()}@student.onlinedegree.iitm.ac.in"
        
        is_member: bool = False
        with open("data", "r") as file:
            if email in file.read():
                is_member = True
        
        return is_member


    @commands.Cog.listener()
    @logger.catch
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name="unverified")
        await member.add_roles(role)

        channel = self.client.get_channel(835853488658841640)
        await channel.send(f"{member.mention} Welcome, you have to verify yourself as member of Saranda House to continue. "
            "Use the command `!verify <IITM register id>` (eg: `!verify 21f1001234`) to continue."
        )

    @commands.command()
    @commands.has_role("unverified")
    @logger.catch
    async def verify(self, ctx, reg_no: str):
        """
        Verify yourself as member of the house, by entering your regno and verifying via email. Enter your IITM ID to verify (eg: !verify 21f1001234)
        """

        logger.debug(f"Command verify: {ctx.message.author}")
        user = ctx.message.author
        userIsMember = any(map(lambda x: x.name == "Member", ctx.message.author.roles))
        if userIsMember:
            return
        
        if not self.check_regno(reg_no):
            await ctx.message.channel.send(f"You are not recognized to be part of Saranda House, contact house members for more details.")
            return
        
        code = str(int(os.urandom(2).hex(), 16))
        if not self.send_mail(f"{reg_no}@student.onlinedegree.iitm.ac.in", code):
            await ctx.message.channel.send(f"{user.mention} Unable to send emails, contact house members for more details.")
            return
        
        try:
            await user.send(f"I have sent an email to `{reg_no}@student.onlinedegree.iitm.ac.in` containing 4 digit verification code. Please enter the 4 digit code to verify yourself. (You have 2 minutes to complete this verificaion)")
            await ctx.message.channel.send(f"{user.mention} Check your DM for further instructions.")
        except:
            await ctx.message.channel.send(f"{user.mention} I am not able to send you DM. Please open your DMs for this server, and try again.")
            return

        def is_user_dm(m):
            return m.author == user and m.channel.type is discord.ChannelType.private

        try:
            auth_code = (await self.client.wait_for('message', check=is_user_dm, timeout=120)).content.strip()
        except:
            await user.send("Verification timeout. You can restart the process by running `!verify` command again.")
            return
        
        if code == auth_code:
            unveri_role = discord.utils.get(ctx.guild.roles, name='unverified')
            await user.remove_roles(unveri_role)
            await user.add_roles(discord.utils.get(ctx.guild.roles, name="Member"))
            await user.send("Verification successful! Welcome to Saranda discord server.")

        else:
            await user.send("Verification unsuccessful. You can try again using `!verify` command.")


def setup(client):
    client.add_cog(Verification(client))
