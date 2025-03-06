import pickle
from pprint import pprint
import operator


def read_totals(repo_file, mainline):
    with open(f"Repos_totals/{str(repo_file)}_{mainline.split('/')[0]}_{mainline.split('/')[1]}_totals.pkl", 'rb') as f:
        return pickle.load(f)

def print_totals(dict_file):
    pprint(dict_file)
    
    
"""
    We need to get the final final decision for each PR based on the number of ED and MO there are. 
    We will also store the number of non-existant files and files with other extensions than the code can handle
"""
# result_dict is now list of dictionaries [{},{}] etc
def final_class(result_dict):  
    total_PA = 0
    total_NE = 0
    total_CC = 0
    total_ERROR = 0
    total_PN = 0

    pr_classes = []
    project = ''
    for elements in result_dict:
        pr, source_file  = next(iter(elements.items()))
        # print(source_file)
        pr_class = {}
        pr_class[pr] = {
            'total_PA' : 0,
            'total_NE' : 0,
            'total_CC' : 0,
            'total_PN' : 0,
            'total_ERROR' : 0,
            'class': ''
        }

        total_PA = 0
        total_NE = 0
        total_CC = 0
        total_PN = 0
        total_ERROR = 0
        class_ = 'None'        
        for file, result in source_file.items():
            # print("Data: ", result['result'])
            for item in result['result']:
                # print("Items: ", item)
                project = item['project']
                try:
                    class_ = item['patchClass']
                    if class_ == 'OTHER EXT':
                        total_CC += 1
                    elif class_ == 'NOT EXISTING':
                        total_NE += 1
                    elif class_ == 'PA':
                        total_PA += 1
                    elif class_ == 'PN':
                        total_PN += 1
                    elif class_ == 'ERROR':
                        total_ERROR += 1
                except:
                    total_ERROR += 1
                # total_E += 1
                
            # print(f'File: {file}, Class: {class_}')
        # print("Total NE: ", total_NE)    
            
        if total_PA==0:
            if total_PN > 0:
                ultimate_class = 'PN'
            else:
                stats = {'CC': total_CC, 'NE': total_NE, 'ERROR': total_ERROR}
                ultimate_class = max(stats.items(), key=operator.itemgetter(1))[0]
        else:
            ultimate_class = 'PA'
            
        
        pr_class[pr] = {
                'totals':
                    {
                        'total_PA' : total_PA,
                        'total_NE' : total_NE,
                        'total_CC' : total_CC,
                        'total_PN' : total_PN,
                        'total_ERROR': total_ERROR
                    },
            'class': ultimate_class,
            'project': project
        }
        pr_classes.append(pr_class)
    return pr_classes

def count_all_classifications(pr_classes):
    all_classes = {}

    all_classes['PA']=0
    all_classes['CC']=0
    all_classes['PN']=0
    all_classes['NE']=0
    all_classes['ERROR']=0
    
    for i in pr_classes:
        key, value  = next(iter(i.items()))
        v = value.get('class')
        if v ==  'NE':
            all_classes['NE'] += 1
        elif v == 'PN':
            all_classes['PN'] += 1
        elif v == 'PA':
            all_classes['PA'] += 1
        elif v == 'CC':
            all_classes['CC'] += 1
        elif v == 'ERROR':
            all_classes['ERROR'] += 1
    return all_classes