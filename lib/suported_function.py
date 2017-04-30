def join_st(st_name, st_ifbase, def_v):
    for i, n in enumerate(st_name):
	if i >= len(st_ifbase):
	    st_ifbase.append(def_v)
