
typesize = {'int': 8, 'bool': 1}

class table_entry:
    def __init__(self, offset, datatype):
        self.offset = offset
        self.datatype = datatype
        self.size = typesize[datatype]

class func_symbol_table:
    def __init__(self, funcname):
        self.funcname = funcname
        self.table = {}
        self.available_stack = [[],[],[],[]]
        self.size = 0
        self.saved_reg = ['lr', 'fp']

    def find_space(self, size):
        offset = -1
        for i in range(4):
            if 2**i >= size and len(self.available_stack[i]) > 0:
                addr = self.available_stack[i][0]
                self.available_stack[i] = self.available_stack[i][1:]
                offset = addr
                left = 2**i - size
                addr += size
                for j in range(3):
                    if 2**j < size:
                        continue
                    if left >= 2**j:
                        self.available_stack[j].append(addr)
                        addr += 2**j
                        left -= 2**j
                break
        return offset

    def alloc_stack(self, size):
        offset = -1
        if size <= 8:
            offset = self.find_space(size)
            if offset == -1:
                self.available_stack[3] += [self.size, self.size+8]
                self.size += 16
                offset = self.find_space(size)
        return offset

    def insert(self, varname, vartype):
        if varname in self.table:
            #if self.table[varname].datatype != vartype:
            return

        offset = self.alloc_stack(typesize[vartype])
        self.table[varname] = table_entry(offset, vartype)

    def get_offset(self, varname):
        if varname in self.table:
            entry = self.table[varname]
            return len(self.saved_reg)*16 + entry.offset
        return None

    def get_type(self, varname):
        if varname in self.table:
            entry = self.table[varname]
            return entry.datatype
        return None

class symbol_table:
    def __init__(self):
        self.table = {}

    def insert(self, funcname, varname, vartype):
        if funcname not in self.table:
            self.table[funcname] = func_symbol_table(funcname)
        self.table[funcname].insert(varname, vartype)

    def get_offset(self, funcname, varname):
        if funcname not in self.table:
            return None
        return self.table[funcname].get_offset(varname)

    def get_type(self, funcname, varname):
        if funcname not in self.table:
            return None
        return self.table[funcname].get_type(varname)

    def size(self, funcname):
        if funcname not in self.table:
            return 0
        return self.table[funcname].size

    def get_regs(self, funcname):
        if funcname not in self.table:
            return None
        return self.table[funcname].saved_reg

    def set_regs(self, funcname, regs):
        if funcname not in self.table:
            return None
        self.table[funcname].saved_reg = regs
