import pandas as pd
import mimetypes
import os,tempfile
import shutil


def clean_upload_data(file,company_obj,dbcolumn:list,Prospect):

    #csv = .xls
    #exce file =.xlsx

    ## check file 
    tempdir = "prospect/data"
    os.makedirs(tempdir,exist_ok=True)
    file_path = os.path.join(tempdir,file.name)

    with open(file_path,"wb") as locations:
        for chunk in file.chunks():
            locations.write(chunk)

    file_type = mimetypes.guess_type(file_path)[0]
    file_extension = mimetypes.guess_extension(file_type)

    if file_extension == ".xls":
        df =  pd.read_csv(file_path,dtype='object')
        print(df.head())
        column = [columns for columns in df.columns]

        if column == dbcolumn:
            df.drop_duplicates(inplace=True)
            
            df.loc[:] = df.loc[:].apply(lambda x:x.str.lower())\
                .fillna("None")
            for obj in df.to_dict(orient='records'):
                    obj['user_company'] = company_obj
                    Prospect.objects.create(**obj)

            shutil.rmtree(os.path.dirname(file_path))
            return True
        else:
            return False
        
    elif file_extension == ".xlsx":
        df =  pd.read_excel(file_path,engine="openpyxl",dtype='str')
        #print(df.head())
        column = [columns for columns in df.columns]
        if column == dbcolumn:
            df.drop_duplicates(inplace=True)
            df.loc[:] = df.loc[:].apply(lambda x:x.str.lower())\
            .fillna("None")

            for obj in df.to_dict(orient='records'):
                    obj['user_company'] = company_obj
                    Prospect.objects.create(**obj)

            shutil.rmtree(os.path.dirname(file_path))
            return True
        else:
            return False







    
      





