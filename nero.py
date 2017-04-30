import numpy as np

def compute_nero(answers, user_weights, teacher_answer, step_lenth=0.04):
    A = np.array(answers)
    w = np.array(user_weights)
    T = teacher_answer
    print A, w
    ans = (sum(A * w) / sum(w) )#+ T) / 2
    new_w = []	
    for ai, wi in zip(A, w):	 	
	Q = (ans - T) * ai
	new_w.append(wi - step_lenth * Q) 
    return T, ans, list(new_w) #T, ans, ai		

if __name__ == "__main__":
    A = [3,2,5,5,0, 10]
    w = [0.1,0.1,0.1,0.1,0.1, 0.1]
    T = 4
    		
    print compute_nero(A, w, T) #slow changing w people.. (all should change slow...speed)

    for i in range(10):
	d = compute_nero(A, w, T)
  	w = d[2]
	print d


#"st_ch":  [true,    false,      true,    true,       false,    false,     false,     true],"st_def":
#	   ["0",    "0.1",       "0",    "0.0",       "0.0",     "0",    "answers 0"],"st_name":	 
			 
#	["jump","lesson_in__W","100m","lesson_in__A","100m__R","jump__R","lesson_in__I","lesson_in"],"st_opt":	
#	["ranking", "w",     "ranking",   "a",       "points","points",    "itr",        "nero"],"return_ch":[]}
