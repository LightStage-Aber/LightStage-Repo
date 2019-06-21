import os
import csv


def makeDirectory(directory):
        if not os.path.exists(directory) and directory != "":
                os.makedirs(directory)


def rename_file(old , new, overwrite=False):
        if os.path.exists(old):
                if overwrite:
                        os.rename(old, new)
                else:
                        if os.path.exists(new):
                                new += "~"
                                print("Specified new filename already exists. Renamed and writing file with filename: "+new)
                        os.rename(old, new)


def write_to_file(s, path, filename, append_newline=True):
        makeDirectory(path)
        f 		= open(path+filename,'a')
        if append_newline:
                f.write( str(s) + "\n")
        else:   
                f.write( str(s) )
        f.close()


def write_to_file_list(strings, path, filename, append_newline=True):
        makeDirectory(path)
        f 		= open(path+filename,'a')
        for s in strings:
            if append_newline:
                    f.write( str(s) +"\n")
            else:   
                    f.write( str(s) )
        f.close()



def write_to_csv(l, path, filename, asRows=False, doAppend=True):
        makeDirectory(path)
        write_mode          = 'a' if doAppend else 'w'
        with open(path+filename,write_mode) as f:
            wr              = csv.writer(f, dialect='excel')
            if not asRows:
                    wr.writerow(l)
            else:
                    wr.writerows(l)

def write_to_latex_table(rows, header, path, filename):
        # pip install tabulate
        from tabulate import tabulate
        s = tabulate(rows, header, tablefmt="latex_booktabs")
        s = s.replace("\\textbackslash{}","\\")
        write_to_file(s, path, filename, append_newline=True)

def read_column(filename, skip_header=False, column_num=0, quantity=0):
        """
        This reads in the entire file, specified by filename. 
        Trucates the file, Separates the specified column and returns.
        """
        l = read_in_csv_file_to_list_of_lists(filename, skip_header)
        l = l[:quantity]
        column = [row[column_num] for row in l]
        return column

def read_in_csv_file_to_list_of_lists(filename, skip_header=False):
        """
        Read in csv file
        """
        if not os.path.exists(filename):
                print("Error: Requested file does not exist: "+str(filename))
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            if skip_header == True:     # either true or 1.
                reader.next()                # skip header
            elif type(skip_header) == int:
                if skip_header > 1:
                        for i in range(skip_header):
                                reader.next()                # skip header
            l = list(reader)
        return l


def read_in_csv_file_header_to_list(filename):
        """
        Read in csv file header only.
        """
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            l = list(reader.next())
        return l


def read_file_to_list(filename):
        """
        Read in file to list of strings
        """
        l = []
        with open(filename, 'rb') as f:
            for line in f:
                l.append( line.strip() )
        return l


class file_writer:
        def __init__(self,path,filename,header=None):
                self.filename   = filename
                self.path       = path
                if header != None:
                        self.write_to_file(header)
        def write_to_file(self, s):
                write_to_file(s, self.path, self.filename)
        def write_to_file_append(self, s):
                write_to_file(s, self.path, self.filename, append_newline=False)
        def write_to_file_list(self, strings, append_newline=True):
                write_to_file_list(strings, self.path, self.filename, append_newline=append_newline)
        def write_to_csv(self, l):
                write_to_csv(l, self.path, self.filename)
        def write_to_csv_rows(self, l):
                write_to_csv(l, self.path, self.filename, asRows=True)
        def get_filepath(self):
                return self.path+self.filename


if __name__ == "__main__":
        print("file_io.py")
        fw = file_writer("","mytest_file.txt")
        fw.write_to_file("hello world")
        fw.write_to_csv( [1,2,3,4,5] )
        fw.write_to_csv( [6,7,8,9,10] )
        fw.write_to_csv_rows( [[1],[2],[3]] )
