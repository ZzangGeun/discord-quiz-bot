import sys                                                                                                                                                                                             


def process_string_by_argument(input_string, argument):                                                                                                                                                                                                   
    """                                                                                                                                                                                                
    주어진 문자열을 '★' 기준으로 나누고, 매개변수에 따라 앞 또는 뒤를 반환합니다.                                                                                                                      
    """                                                                                                                                                                                                
    # 입력 문자열이 None이거나 빈 문자열인 경우 처리
    if not input_string:
        return "❌ 빈 문자열입니다."
    
    parts = input_string.split('★', 1) # '★' 구분자로 최대 1번만 분리합니다.                                                                                                                           
    if argument == '1':                                                                                                                                                                                
        if len(parts) > 0:                                                                                                                                                                             
            return parts[0].strip() # 구분자 앞부분                                                                                                                                                            
        else:                                                                                                                                                                                          
            return "❌ 문자열에 내용이 없습니다."                                                                                                                                                         
    elif argument == '2':                                                                                                                                                                              
        if len(parts) > 1:                                                                                                                                                                             
            # '답:' 부분을 제거하고 실제 답만 반환
            answer_part = parts[1].strip()
            if answer_part.startswith('답:') or answer_part.startswith('답 :'):
                answer_part = answer_part.replace('답:', '', 1).replace('답 :', '', 1).strip()
            return answer_part # 구분자 뒷부분                                                                                                                                                            
        elif len(parts) == 1 and '★' not in input_string: # 구분자가 없는 경우 전체 문자열이 parts[0]에 들어감                                                                                         
            return "❌ 구분자('★')가 없어 답을 찾을 수 없습니다."                                                                                                                       
        else: # 구분자는 있으나 뒷부분이 없는 경우 (예: "text★")                                                                                                                                       
            return "❌ 답 부분이 없습니다." # 빈 문자열 반환 또는 "뒷부분이 없습니다." 등의 메시지                                                                                                                           
    else:                                                                                                                                                                                              
        return "❌ 잘못된 매개변수입니다. 1 또는 2를 입력해야 합니다."
#파일 읽어오기                                                                                                                                                                                         
def read_string_from_file(file_path="cote_bot.txt"):                                                                                                                                              
    """                                                                                                                                                                                                
    파일에서 문자열을 읽어옵니다.                                                                                                                                                                      
    """                                                                                                                                                                                                
    try:                                                                                                                                                                                               
        with open(file_path, 'r', encoding='utf-8') as file:                                                                                                                                           
            content = file.read().strip() # strip()으로 앞뒤 공백 제거                                                                                                                                 
            return content                                        
    except FileNotFoundError:                                                                                                                                                                          
        print(f"정보: '{file_path}' 파일을 찾을 수 없어 기본 문자열을 사용합니다.")                                                                                                                    
        return "기본 문자열 앞부분★기본 문자열 뒷부분" # 파일이 없을 경우 사용할 예시 문자열                                                                                                           
    except IOError:                                                                                                                                                                                    
        print(f"'{file_path}' 파일을 읽는 중 오류가 발생하여 기본 문자열을 사용합니다.")                                                                                                               
        return "오류 발생 시 문자열★대체 뒷부분"