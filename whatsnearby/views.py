import os
import unicodecsv
import random
from pyramid.response import Response, FileResponse
from pyramid.view import view_config
from sqlalchemy.exc import DBAPIError

from .models import (
	DBSession,
	MyModel,
	)


@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):
	return {'name' : 'whatsnearby'}


@view_config(route_name='result', request_method='POST', request_param="submit_files", renderer='templates/result.jinja2')
def result_view(request):
	gene_file_name = request.POST['gene_file'].filename
	gene_file = request.POST['gene_file'].file
	
	dnase_file_name = request.POST['dnase_file'].filename
	dnase_file = request.POST['dnase_file'].file
	outfile_name = ''
	ext_gene_file = os.path.splitext(gene_file_name)[-1].lower()
	ext_dnase_file = os.path.splitext(dnase_file_name)[-1].lower()
	if(ext_gene_file == ".bed" and ext_dnase_file == ".bed"):
		outfile_name = find_overlapping(gene_file, dnase_file)
	return {'download' : outfile_name}
	
@view_config(route_name='download', request_method ="GET")	
def download_view(request):
	return FileResponse("/tmp/nihlib/" + request.matchdict['file_name'])
	
	
def find_overlapping(file_gene, file_dnase):
	rand_name = str(random.randint(1, 100000)) + ".csv"
	outfile = "/tmp/nihlib/" + "overlapping" + rand_name
	out = open(outfile, 'wb')
	writer = unicodecsv.writer(out)
	writer.writerow(['Chr', 'TranscriptStart', 'TrascriptStop', 'TranscriptID', 'Strand', 'DNaseStart', 'DNaseStop', 'DNaseID'])
	
	dnase_lines = file_dnase.readlines();
	gene_cntr = 0
	for gene_line in file_gene:
		gene_cntr += 1
		if gene_cntr == 1:
			continue
		gene = gene_line.decode('utf8')
		elements = gene.split("\t")
		geneChr = elements[0]
		geneStart = int(elements[1])
		geneStop = int(elements[2])
		geneId = elements[3]
		strand = elements[5]
		geneLength = geneStop - geneStart

		dnase_cntr = 0
		for dnase_line in dnase_lines:
			dnase_cntr += 1
			if(dnase_cntr == 1):
				continue
			dnase = dnase_line.decode('utf8')
			dnaseElements = dnase.split("\t")
			dnaseChr = dnaseElements[0]
			dnaseStart = int(dnaseElements[1])
			dnaseStop = int(dnaseElements[2])
			dnaseId = dnaseElements[3]
			dnaseLength = dnaseStop - dnaseStart
			
			if(dnaseChr == geneChr):
				if(dnaseStart == geneStart and dnaseStop == geneStop):
					writer.writerow([geneChr, geneStart ,geneStop, geneId, strand, dnaseStart, dnaseStop, dnaseId])
				elif(dnaseStart >= geneStart and dnaseStart <= geneStop):
					writer.writerow([geneChr, geneStart ,geneStop, geneId, strand, dnaseStart, dnaseStop, dnaseId])
				elif(dnaseStop >= geneStart and dnaseStop <= geneStop):
					writer.writerow([geneChr, geneStart ,geneStop, geneId, strand, dnaseStart, dnaseStop, dnaseId])
				elif(geneStart >= dnaseStart and geneStart <= dnaseStop):
					writer.writerow([geneChr, geneStart ,geneStop, geneId, strand, dnaseStart, dnaseStop, dnaseId])
						
	file_gene.close()
	file_dnase.close()
	out.close()
	
	return os.path.basename(outfile)