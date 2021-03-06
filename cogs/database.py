import discord
from discord.ext import commands
from discord.ext import tasks

import json
import sqlalchemy.orm.query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound


from models.base import Base, Session, engine
from models.post import Post
from models.role import Role
from models.user import User
from models.channel import Channel
from models.youtube import Youtube
import models.base as base

import datetime

from utils import misc


class Database(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.detect_anomalies.start()

        Base.metadata.create_all(engine)
        self.session = Session()
        

    def Session(self):
        return base.Session()

    @commands.command()
    @commands.has_any_role('Administrator') 
    async def report(self, ctx):
        """Log users that are not in the database."""

        f = open("report.txt", "w", encoding='utf-8')
        for guild in self.client.guilds:                                                        
            for member in guild.members:
                role = guild.get_role(499945447616544798) # quick fix
                if role not in member.roles:
                    try:
                        user = self.session.query(User) \
                                .filter(User.UserId == member.id) \
                                .one()
                    except SQLAlchemyError:
                        f.write("-----------------------------------------------------\n")
                        name = member.nick if member.nick is not None else member.name
                        f.write(name + ": \n")
                        f.write("$add-member @" + member.name + "#" + member.discriminator + "\n")
        f.close()
                
    @commands.command(aliases=["insert-channel"], description = "Add channel to the database")
    @commands.has_any_role('Administrator') 
    async def insert_channel(self, ctx, channel: discord.TextChannel):
        """Insert channel into database."""

        try:
            newChannel = Channel(channel.id, channel.name)
            self.session.add(newChannel)
            self.session.commit()
        except SQLAlchemyError as err:
            await ctx.send(str(err))
            self.session.rollback()

    @commands.command(aliases=["insert-role"], description = "Add role to the database")
    @commands.has_any_role('Administrator')   
    async def insert_role(self, ctx, role: discord.Role):
        """Insert role into database."""

        try:
            new_role = Role(role.id, role.name)
            self.session.add(new-role)
            self.session.commit()
        except SQLAlchemyError as err:
            await ctx.send(str(err))
            self.session.rollback()
            

    @commands.command()
    @commands.has_any_role('Administrator', 'Moderator')
    async def whois(self, ctx, user: discord.User):
        """Get info of user by mention."""

        try:
            member = misc.getMember(self.client, user.id)

            embed = discord.Embed(
                description = member.mention
            )

            embed.set_author(name = member.display_name, icon_url = member.avatar_url)
            embed.set_thumbnail(url = member.avatar_url)
            embed.add_field(
                name = "Registered",
                value = user.created_at.strftime("%a, %b %d, %Y,\n %H:%M %p")
            )

            embed.add_field(
                name = "Joined",
                value = member.joined_at.strftime("%a, %b %d, %Y,\n %H:%M %p")
            )

            roles = [role.mention for role in member.roles[::-1] if role.name != '@everyone']
            embed.add_field(
                name = "Roles",
                value = ' '.join(roles),
                inline = False
            )
            
            await ctx.send(embed = embed)

            
        except NoResultFound as err:
            await ctx.send(str(err))
        
            

    @commands.command()
    @commands.has_any_role('Administrator', 'Moderator')
    async def student(self, ctx, user_index):
        """Get info of user by student index."""

        try:
            user = self.session.query(User) \
                    .filter(User.UserIndex == user_index) \
                    .one()
            
            member = misc.getMember(self.client, user.UserId)

            embed = discord.Embed(
                description = member.mention
            )

            embed.set_author(name = member.display_name, icon_url = member.avatar_url)
            embed.set_thumbnail(url = member.avatar_url)
            embed.add_field(
                name = "Index",
                value = user.UserIndex
            )

            embed.add_field(
                name = "Discord status",
                value = user.StatusDiscord
            )

            roles = [role.mention for role in member.roles[::-1] if role.name != '@everyone']
            embed.add_field(
                name = "Roles",
                value = ' '.join(roles),
                inline = False
            )
            
            await ctx.send(embed = embed)

        except NoResultFound as err:
            await ctx.send(str(err))

        self.session.rollback()


    @tasks.loop(hours = 7 * 24)
    async def detect_anomalies(self):
        print("Anomalysing...")

        f = open("report-anomalys.txt", "w", encoding='utf-8')

        all_roles = self.session.query(Role).all()
        
        for guild in self.client.guilds:                                                        
            for member in guild.members:
                role = guild.get_role(499945447616544798) # quick fix
                if role not in member.roles:
                    try:
                        user = self.session.query(User) \
                                .filter(User.UserId == member.id) \
                                .one()

                        if user is not None:
                            # if member.nick is None:
                            #     user.Name = member.name
                            if user.Name != member.nick:
                                if member.nick is not None:
                                    user.Name = member.nick
 
                            if user.Username != member.name:
                                user.Username = member.name
                                
                            if user.Discriminator != member.discriminator:
                                user.Discriminator = member.discriminator

                            # Users roles in database
                            userRolesIDs = [role.RoleId for role in user.Roles]
                            # Users actual roles in discord
                            memberRolesIDs = [role.id for role in member.roles]
                            
                            
                            for db_role in all_roles:
                                if db_role.RoleId in memberRolesIDs:
                                    if db_role.RoleId not in userRolesIDs:
                                        try:
                                            self.session.commit()
                                        except Exception as err:
                                            print(err)
                                            self.session.rollback()
                                elif db_role.RoleId in userRolesIDs:
                                    if db_role.RoleId not in memberRolesIDs:
                                        try:
                                            user.Roles.remove(db_role)
                                            self.session.commit()
                                        except Exception as err:
                                            print(err)
                                            self.session.rollback()

                        self.session.commit()
                    except SQLAlchemyError as err:
                        print(err)
                        print(member.name)
                        f.write("$add-member @" + member.name + "#" + member.discriminator + "\n")
                        self.session.rollback()
        f.close()
                

    def cog_unload(self):
        self.detect_anomalies.cancel()

    @detect_anomalies.before_loop
    async def before_detect_anomalies(self):
        print('Database: Waiting...')
        await self.client.wait_until_ready()


def setup(client):
    client.add_cog(Database(client))

