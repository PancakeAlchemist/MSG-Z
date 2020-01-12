import discord
from discord.ext import commands, tasks


import sqlalchemy.orm.query
from sqlalchemy.exc import SQLAlchemyError

import models.tag as tg
from models.user import User

class Tag(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["add-tag"])
    async def add_tag(self, ctx, url: str, *name: str):
        tag_name = ' '.join(name)
        database = self.client.get_cog('Database')
        if database is not None:
            try:
                session = database.Session()

                user = session.query(User) \
                        .filter(User.UserId == ctx.author.id) \
                        .one()


                newTag = tg.Tag(tag_name, url, user)
                session.add(newTag)
                session.commit()

                await ctx.send("Tag added")
            except SQLAlchemyError as err:
                print(str(err))
                session.rollback()
            finally:
                session.close()

    @commands.command(aliases=["remove-tag"])
    @commands.has_any_role('Administrator', 'Moderator')
    async def remove_tag(self, ctx, id: int):
        database = self.client.get_cog('Database')
        if database is not None:
            try:
                session = database.Session()
                tag = session.query(tg.Tag) \
                    .filter(tg.Tag.Id == id) \
                    .one()
                session.delete(tag)
                session.commit()

                await ctx.send("Tag removed")
            except SQLAlchemyError as err:
                print(str(err))
                session.rollback()
            finally:
                session.close()


    @commands.command(aliases=["rename-tag"])
    @commands.has_any_role('Administrator', 'Moderator')
    async def rename_tag(self, ctx, id: int, *name: str):
        tag_name = ' '.join(name)
        database = self.client.get_cog('Database')
        if database is not None:
            try:
                session = database.Session()
                tag = session.query(tg.Tag) \
                    .filter(tg.Tag.Id == id) \
                    .one()
                tag.Name = tag_name
                session.commit()

                await ctx.send("Tag renamed")
            except SQLAlchemyError as err:
                print(str(err))
            finally:
                session.close()

    @commands.command(aliases=["tag"])
    async def get_tag(self, ctx, *, search: str):
        database = self.client.get_cog('Database')
        if database is not None:
            session = database.Session()
            tags = session.query(tg.Tag) \
                .filter(tg.Tag.Name.ilike(f"%{search}%"))


            description = '\n'
            for tag in tags:
                description += f"\n{tag.Id}. [{tag.Name}]({tag.Link})"
                tag.Count += 1
                              
            embed = discord.Embed(
                title = "Tags",
                description = description,
                colour = discord.Colour.blurple().value
            ) 
            
            await ctx.send(embed = embed)
            session.commit()
            session.close()

def setup(client):
    client.add_cog(Tag(client))
