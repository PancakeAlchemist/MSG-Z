import discord

class DLWMS_Notification:
    def __init__(self, link, title, date, subject, author, mail, content):
        self.link = link
        self.title = title
        self.date = date
        self.subject = subject
        self.author = author
        self.mail = mail
        self.content = content
        
    def __str__(self):
        return "Naslov: " + self.title + \
               "\nDatum: " + self.date + \
               "\nAutor: " + self.author + \
               "\nMail: " + self.mail + \
               "\nObavijest: " + self.content + "\n"

    def getEmbed(self):
        embed = discord.Embed(
            title = self.title,
            url = self.link,
            colour = discord.Colour.blue().value
        )

        embed.add_field(
            name = "Obavijest",
            value = self.content
        )

        embed.add_field(
            name = "Info",
            value = "Datum: {}\nAutor: {}\nMail: {}".format(self.date, self.author, self.mail)
        )

        return embed
        
    
    def __eq__(self, other):
        return self.link == other.link and \
               self.title == other.title and \
               self.date == other.date and \
               self.subject == other.subject and \
               self.author == other.author and \
               self.mail == other.mail

# class Discord_Bot_Notification:
#     def __init__(self, author, title, desctiption, date, colour):
#         self.author = author
#         self.title = title,
#         self.desctiption = desctiption,
#         self.date = date,
#         self.colour = colour

    
