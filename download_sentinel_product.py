""" Class for downloading content from url

AUTHOR: Trygve Halsne 06.03.2017

REVISION: N/A

STATUS:
    - Works only for Sentinel SAFE products
    - Needs a more sophisticated implementation if to work for other prodcts
"""

import glob
import urllib2 as ul2
import lxml.etree as ET
import sys

class Download_url():
    """ Class generating object for downloading content from url """
    def __init__(self, url, username, password, output_path, uuid):
        self.url = url
        self.username = username
        self.password = password
        self.output_path = output_path
        self.uuid = uuid

    def download(self):
        url, uname, pw, output_path = self.url, self.username, self.password, self.output_path
        try:
            print "\n\tReading data for download:"
            print '\t',url
            p = ul2.HTTPPasswordMgrWithDefaultRealm()
            p.add_password(None, url, uname, pw)
            handler = ul2.HTTPBasicAuthHandler(p)
            opener = ul2.build_opener(handler)
            ul2.install_opener(opener)
            f = ul2.urlopen(url,timeout = 60*60*2)
            info = f.info()
            header = info.getheader('Content-Disposition')
            output_fname = header.split('"')[1]
            output_complete = str(output_path + output_fname)
            print "\tDataset: %s " % output_fname
            print "\tWriting dataset to: %s" % output_path

            CHUNK_SIZE = 1024 * 1024 # 1MB
            total_size = int(info.getheader('Content-Length'))
            total_size_readable = total_size/float(CHUNK_SIZE)

            if total_size > 0:
                with open(output_complete,'w') as op:
                    data = 'first'
                    progress_size = 0
                    while len(data) > 0:
                        data = f.read(CHUNK_SIZE)
                        progress_size += len(data)
                        progress_size_percent = ((progress_size/float(CHUNK_SIZE))/total_size_readable)*100
                        print '\tPercent complete:', "%.5f" % progress_size_percent, '\r',
                        op.write(data)
                    print '\n'

            print "\tFinished downloading"
            return True, output_fname
        except IOError as e:
            print "I/O error({0}): {1}".format(e.errno, e.strerror)
            return False

def main():

    # Only made for OpenSearch ENTRY files
    filepath = "/home/trygveh/documents/nbs/metadata_harvesting/output/"

    xml_files = glob.glob(str(filepath + '*.xml'))

    with open('/home/trygveh/documents/nbs/metadata_harvesting/myValues.txt','r') as code:
        cred_tmp = code.readline()

    cred = cred_tmp.split(';')

    uname = cred[0]
    pw = cred[1]
    output_path = "downloads/"
    baseURL_start = "https://colhub.met.no/odata/v1/Products('"
    baseURL_end = "')/$value"

    counter = 0
    for xml_file in reversed(xml_files):
        xml_file_ET = ET.parse(xml_file)
        xml_tree = xml_file_ET.getroot()
        uuid = xml_tree.xpath('.//str[@name="uuid"]')[0].text
        URL = str(baseURL_start + uuid + baseURL_end)
        dload_object = Download_url(URL,uname,pw,output_path,uuid)
        download_OK, op_fname = dload_object.download()
        print download_OK

        #d, fname = dload_object.download()
        #dload_object.write_to_file(data=d,output_fname=fname)


        if counter == 2:
            break
        counter += 1

if __name__ == '__main__':
    main()
