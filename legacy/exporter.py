import csv
import logging

logger = logging.getLogger(__name__)

class LegacyUserDetailsExporter():
    """
    Extracts all user information from CSV export
    (matching needs to be done manually later)
    
    ks__vorgang:letzter_bearbeiter, ks_kommentar
    ks_lob_hinweise_kritik:empfaenger_email
    klarschiff_benutzer
    
    """
    def __init__(self, cmd):
        self.cmd = cmd
        fullnames = self._readCSVrow("klarschiff_vorgang.csv",'letzter_bearbeiter', 'fullnames')
        emails = self._readCSVrow("klarschiff_lob_hinweise_kritik.csv",'empfaenger_email', 'emails')
        # splitup multiple mail receivers
        temp = set()
        for mail in emails:
            if mail.find(',') > -1:
                mails = mail.split(',')
                temp.update(mails)
            else:
                temp.add(mail)
        emails = temp
        usernames = self._readCSVrow("klarschiff_benutzer.csv",'benutzername', 'usernames')
        self._saveLists('users.txt',[fullnames, emails, usernames])
        
        
    
    def _readCSVrow(self, csvfilename, rowname, infoname):
        """Open CSV and return unique values of given column"""
        logger.debug('opening {}'.format(csvfilename))
        csvfile = open(csvfilename)
        reader = csv.DictReader(csvfile)
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Reading {} ...'.format(csvfilename)))
        fullnames=set()
        for row in reader:
            fullnames.add(row[rowname])
        self.cmd.stdout.write(self.cmd.style.SUCCESS('Found {} unique {}'.format(len(fullnames), infoname)))
        return fullnames
    
    def _saveLists(self,listfilename,lists):
        lsfile = open(listfilename, 'w')
        for ls in lists:
            lsfile.write('----\n')
            ls = list(ls)
            ls.sort()
            for x in ls:
                lsfile.write(x+'\n')
        lsfile.close()
