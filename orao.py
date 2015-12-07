 # -*- coding: utf8 -*-
import pygame, numpy, sys, datetime, wave, time

class CPU(object):
    CARRY, ZERO, INTERRUPT, DECIMAL, BREAK, UNUSED, OVERFLOW, NEGATIVE = [2**i for i in range(8)]

    def __init__(self, memory):
        s, self.tape_out, self.filename, self.samples = self, None, None, 0
        s.memory, s.tape, s.flipflop, s.last_sound_cycles, s.sndbuf = memory, None, 0, -20000, []
        s.cycles, s.pc, s.flags, s.sp, s.a, s.x, s.y = 0, 0xFF89, 48, 0xFF, 0, 0, 0

        s._opcodes = {       0x00:(s.BRK,s.no,7), 0x01:(s.ORA,s.ix,6), 0x05:(s.ORA,s.zp,3),
        0x06:(s.ASL,s.zp,5), 0x08:(s.PHP,s.no,3), 0x09:(s.ORA,s.im,2), 0x0a:(s.ASL,s.no,2),
        0x0d:(s.ORA,s.ab,4), 0x0e:(s.ASL,s.ab,6), 0x10:(s.BPL,s.re,4), 0x11:(s.ORA,s.iy,6),
        0x15:(s.ORA,s.zx,4), 0x16:(s.ASL,s.zx,6), 0x18:(s.CLC,s.no,2), 0x19:(s.ORA,s.ay,5),
        0x1d:(s.ORA,s.ax,5), 0x1e:(s.ASL,s.ax,7), 0x20:(s.JSR,s.jm,6), 0x21:(s.AND,s.ix,6),
        0x24:(s.BIT,s.zp,3), 0x25:(s.AND,s.zp,3), 0x26:(s.ROL,s.zp,5), 0x28:(s.PLP,s.no,4),
        0x29:(s.AND,s.im,2), 0x2a:(s.ROL,s.no,2), 0x2c:(s.BIT,s.ab,4), 0x2d:(s.AND,s.ab,4),
        0x2e:(s.ROL,s.ab,6), 0x30:(s.BMI,s.re,4), 0x31:(s.AND,s.iy,6), 0x35:(s.AND,s.zx,4),
        0x36:(s.ROL,s.zx,6), 0x38:(s.SEC,s.no,2), 0x39:(s.AND,s.ay,5), 0x3d:(s.AND,s.ax,5),
        0x3e:(s.ROL,s.ax,7), 0x40:(s.RTI,s.no,6), 0x41:(s.EOR,s.ix,6), 0x45:(s.EOR,s.zp,3),
        0x46:(s.LSR,s.zp,5), 0x48:(s.PHA,s.no,3), 0x49:(s.EOR,s.im,2), 0x4a:(s.LSR,s.no,2),
        0x4c:(s.JMP,s.jm,3), 0x4d:(s.EOR,s.ab,4), 0x4e:(s.LSR,s.ab,6), 0x50:(s.BVC,s.re,4),
        0x51:(s.EOR,s.iy,6), 0x55:(s.EOR,s.zx,4), 0x56:(s.LSR,s.zx,6), 0x58:(s.CLI,s.no,2),
        0x59:(s.EOR,s.ay,5), 0x5d:(s.EOR,s.ax,5), 0x5e:(s.LSR,s.ax,7), 0x60:(s.RTS,s.no,6),
        0x61:(s.ADC,s.ix,6), 0x65:(s.ADC,s.zp,3), 0x66:(s.ROR,s.zp,5), 0x68:(s.PLA,s.no,4),
        0x69:(s.ADC,s.im,2), 0x6a:(s.ROR,s.no,2), 0x6c:(s.JMP,s.id,5), 0x6d:(s.ADC,s.ab,4),
        0x6e:(s.ROR,s.ab,6), 0x70:(s.BVS,s.re,3), 0x71:(s.ADC,s.iy,6), 0x75:(s.ADC,s.zx,4),
        0x76:(s.ROR,s.zx,6), 0x78:(s.SEI,s.no,2), 0x79:(s.ADC,s.ay,5), 0x7d:(s.ADC,s.ax,5),
        0x7e:(s.ROR,s.ax,7), 0x81:(s.STA,s.ix,6), 0x84:(s.STY,s.zp,3), 0x85:(s.STA,s.zp,3),
        0x86:(s.STX,s.zp,3), 0x88:(s.DEY,s.no,2), 0x8a:(s.TXA,s.no,2), 0x8c:(s.STY,s.ab,4),
        0x8d:(s.STA,s.ab,4), 0x8e:(s.STX,s.ab,4), 0x90:(s.BCC,s.re,4), 0x91:(s.STA,s.iy,6),
        0x94:(s.STY,s.zx,4), 0x95:(s.STA,s.zx,4), 0x96:(s.STX,s.zy,4), 0x98:(s.TYA,s.no,2),
        0x99:(s.STA,s.ay,5), 0x9a:(s.TXS,s.no,2), 0x9d:(s.STA,s.ax,5), 0xa0:(s.LDY,s.im,2),
        0xa1:(s.LDA,s.ix,6), 0xa2:(s.LDX,s.im,2), 0xa4:(s.LDY,s.zp,3), 0xa5:(s.LDA,s.zp,3),
        0xa6:(s.LDX,s.zp,3), 0xa8:(s.TAY,s.no,2), 0xa9:(s.LDA,s.im,2), 0xaa:(s.TAX,s.no,2),
        0xac:(s.LDY,s.ab,4), 0xad:(s.LDA,s.ab,4), 0xae:(s.LDX,s.ab,4), 0xb0:(s.BCS,s.re,4),
        0xb1:(s.LDA,s.iy,6), 0xb4:(s.LDY,s.zx,4), 0xb5:(s.LDA,s.zx,4), 0xb6:(s.LDX,s.zy,4),
        0xb8:(s.CLV,s.no,2), 0xb9:(s.LDA,s.ay,5), 0xba:(s.TSX,s.no,2), 0xbc:(s.LDY,s.ax,5),
        0xbd:(s.LDA,s.ax,5), 0xbe:(s.LDX,s.ay,5), 0xc0:(s.CPY,s.im,2), 0xc1:(s.CMP,s.ix,6),
        0xc4:(s.CPY,s.zp,3), 0xc5:(s.CMP,s.zp,3), 0xc6:(s.DEC,s.zp,5), 0xc8:(s.INY,s.no,2),
        0xc9:(s.CMP,s.im,2), 0xca:(s.DEX,s.no,2), 0xcc:(s.CPY,s.ab,4), 0xcd:(s.CMP,s.ab,4),
        0xce:(s.DEC,s.ab,3), 0xd0:(s.BNE,s.re,4), 0xd1:(s.CMP,s.iy,6), 0xd5:(s.CMP,s.zx,4),
        0xd6:(s.DEC,s.zx,6), 0xd8:(s.CLD,s.no,2), 0xd9:(s.CMP,s.ay,5), 0xdd:(s.CMP,s.ax,5),
        0xde:(s.DEC,s.ax,7), 0xe0:(s.CPX,s.im,2), 0xe1:(s.SBC,s.ix,6), 0xe4:(s.CPX,s.zp,3),
        0xe5:(s.SBC,s.zp,3), 0xe6:(s.INC,s.zp,5), 0xe8:(s.INX,s.no,2), 0xe9:(s.SBC,s.im,2),
        0xea:(s.NOP,s.no,2), 0xec:(s.CPX,s.ab,4), 0xed:(s.SBC,s.ab,4), 0xee:(s.INC,s.ab,6),
        0xf0:(s.BEQ,s.re,4), 0xf1:(s.SBC,s.iy,6), 0xf5:(s.SBC,s.zx,4), 0xf6:(s.INC,s.zx,6),
        0xf8:(s.SED,s.no,2), 0xf9:(s.SBC,s.ay,5), 0xfd:(s.SBC,s.ax,5), 0xfe:(s.INC,s.ax,7)}

        s._kbd = {0x83FE: (112, 240, 185, 39),  0x83FF: (45,  48),   # [p đ š ;]  [-  0]
                  0x85FE: (232, 230, 190, 43),  0x85FF: (8,   94),   # [č ć ž :]  [BS ^]
                  0x86FE: (102, 104, 103, 110), 0x86FF: (98,  118),  # [f h g n]  [b  v]
                  0x877E: (100, 97,  115, 122), 0x877F: (120, 99),   # [d a s z]  [x  c]
                  0x87BE: (108, 106, 107, 109), 0x87BF: (44,  46),   # [l j k m]  [,  .]
                  0x87DE: (101, 113, 119, 49),  0x87DF: (50,  51),   # [e q w l]  [2  3]
                  0x87EE: (111, 105, 117, 55),  0x87EF: (56,  57),   # [o i u 7]  [8  9]
                  0x87F6: (114, 121, 116, 54),  0x87F7: (53,  52),   # [r y t 6]  [5  4]
                  0x87FA: (282, 283, 284, 285), 0x87FD: (13,  306),  # [f1f2f3f4] [cr l_ctrl]
                  0x87FC: (276, 273, 274, 275), 0x87FB: (32,  304)}  # [arrows]   [spc l_shift]

        s.ticks = {s.im: 1, s.zp: 1, s.zx: 1, s.zy: 1, s.ab: 2, s.ax: 2, s.no: 0,
                   s.ay: 2, s.jm: 2, s.id: 2, s.ix: 1, s.iy: 1, s.re: 1}

        self.screen = pygame.display.set_mode((800, 900))
        self.terminal = pygame.Surface((256, 256), pygame.SRCALPHA, depth=32)
        self.terminal.fill((255, 255, 255))
        self.alphaarray = pygame.surfarray.pixels_alpha(self.terminal)

        self.background = pygame.image.load("pozadina.png").convert_alpha()

    def get_flag(self, flag): return self.flags & flag != 0

    def set_flag(self, flag, boolean):
        self.flags = self.flags | flag if boolean else self.flags & ~(flag)

    def set_nz(self, src):
        self.set_flag(self.ZERO, src & 0xFF == 0)
        self.set_flag(self.NEGATIVE, src & 0x80)
        return src

    def get_word(self, addr): return 256 * self.get_byte(addr + 1) + self.get_byte(addr)

    def get_filename(self): return 'wav/{0}.WAV'.format(str(self.memory[592:602]).rstrip())

    def speaker(self):
        self.flipflop ^= 1

        self.samples = int((self.cycles - self.last_sound_cycles) / 22.675)
        if 1 < self.samples < 1000:                                   # Ogranici frekventno podrucje
            self.sndbuf += [255] * self.samples + [0] * self.samples
        self.last_sound_cycles = self.cycles

    def get_byte(self, addr):
        if addr == 0x87FF:                                           # Adresa ulaza kasetofona
            if not self.tape:
                self.tape = (255*(ord(j)>128) for i in \
                    wave.open(self.get_filename()).readframes(2**24) for j in 2*i)

            try:
                return self.tape.next()

            except StopIteration:
                self.tape = None
                return 0x00

        if addr == 0x8800: self.speaker()                           # Zvucnik
        return self.memory[addr] if addr is not None else self.a

    def store_byte(self, addr, val):
        if addr is None:                                            # Akumulator
            self.a = val & 0xFF
            return

        if addr == 0x8800: self.speaker()                           # Zvucnik
        if 0x6000 <= addr <= 0x7FFF:                                # Video RAM
            y, x = divmod((addr - 0x6000) * 8, 256)
            for i in range(8):
                self.alphaarray[x+i, y] = 255 if (val>>i) & 1 else 0    # Transparency mask

        self.memory[addr] = val & 0xFF

    def stack_push(self, value):
        self.store_byte(256 + self.sp, value & 0xFF)
        self.sp = (self.sp - 1) & 0xFF

    def stack_pop(self):
        self.sp = (self.sp + 1) & 0xFF
        return self.get_byte(256 + self.sp)

    def stack_push_word(self, val): map(self.stack_push, [(val >> 8) & 0xFF, val & 0xFF])

    def stack_pop_word(self): return self.stack_pop() + (self.stack_pop() << 8)
    ###########################################################################
    # Adresni nacini
    def im(self): return self.pc
    def zp(self): return self.get_byte(self.pc)
    def zx(self): return (self.zp() + self.x) & 0xFF
    def zy(self): return (self.zp() + self.y) & 0xFF
    def ab(self): return self.get_word(self.pc)
    def ax(self): return (self.ab() + self.x) & 0xFFFF
    def ay(self): return (self.ab() + self.y) & 0xFFFF
    def ix(self): return self.get_word((self.zp() + self.x) & 0xFF)
    def iy(self): return (self.get_word(self.zp()) + self.y) & 0xFFFF
    def id(self): return self.get_word(self.ab())
    def jm(self): return self.ab()
    def no(self): return None

    def re(self):
        loc = self.zp()
        addr = loc - 256 * (loc > 127) if loc & self.NEGATIVE else loc
        return (self.pc + addr) & 0xFFFF
    ###########################################################################
    # Instrukcije
    def TAX(self, d): self.x = self.set_nz(self.a)
    def TXA(self, d): self.a = self.set_nz(self.x)
    def TAY(self, d): self.y = self.set_nz(self.a)
    def TYA(self, d): self.a = self.set_nz(self.y)
    def TSX(self, d): self.x = self.set_nz(self.sp)
    def TXS(self, d): self.sp = self.x

    def LDA(self, addr): self.a = self.set_nz(self.get_byte(addr))
    def LDX(self, addr): self.x = self.set_nz(self.get_byte(addr))
    def LDY(self, addr): self.y = self.set_nz(self.get_byte(addr))
    def STA(self, addr): self.store_byte(addr, self.a)
    def STX(self, addr): self.store_byte(addr, self.x)
    def STY(self, addr): self.store_byte(addr, self.y)

    def AND(self, addr): self.a = self.set_nz(self.get_byte(addr) & self.a)
    def ORA(self, addr): self.a = self.set_nz(self.get_byte(addr) | self.a)
    def EOR(self, addr): self.a = self.set_nz(self.get_byte(addr) ^ self.a)

    def CLC(self, d): self.set_flag(self.CARRY, False)
    def SEC(self, d): self.set_flag(self.CARRY, True)
    def CLD(self, d): self.set_flag(self.DECIMAL, False)
    def SED(self, d): self.set_flag(self.DECIMAL, True)
    def CLI(self, d): self.set_flag(self.INTERRUPT, False)
    def SEI(self, d): self.set_flag(self.INTERRUPT, True)
    def CLV(self, d): self.set_flag(self.OVERFLOW, False)

    def INX(self, d): self.x = self.set_nz((self.x + 1) & 0xFF)
    def INY(self, d): self.y = self.set_nz((self.y + 1) & 0xFF)
    def DEX(self, d): self.x = self.set_nz((self.x - 1) & 0xFF)
    def DEY(self, d): self.y = self.set_nz((self.y - 1) & 0xFF)

    def INC(self, addr): self.store_byte(addr, self.set_nz(self.get_byte(addr) + 1))
    def DEC(self, addr): self.store_byte(addr, self.set_nz(self.get_byte(addr) - 1))

    def ASL(self, addr):
        operand = self.get_byte(addr)
        self.set_flag(self.CARRY, operand & 0x80)
        operand = (operand << 1) & 0xFE
        self.store_byte(addr, self.set_nz(operand))

    def BIT(self, addr):
        op = self.get_byte(addr)
        self.set_flag(self.ZERO, op & self.a == 0)
        self.set_flag(self.NEGATIVE, op & self.NEGATIVE)
        self.set_flag(self.OVERFLOW, op & self.OVERFLOW)

    def PHP(self, d): self.stack_push(self.flags | self.BREAK | self.UNUSED)
    def PHA(self, d): self.stack_push(self.a)
    def PLP(self, d): self.flags = self.stack_pop()
    def PLA(self, d): self.a = self.set_nz(self.stack_pop())
    def NOP(self, d): pass

    def ROR(self, addr):
        value = self.get_byte(addr) >> 1 | self.get_flag(self.CARRY) * 128
        self.set_flag(self.CARRY, self.get_byte(addr) & 1)
        self.store_byte(addr, self.set_nz(value))

    def ROL(self, addr):
        value = self.get_byte(addr) * 2 + self.get_flag(self.CARRY)
        self.set_flag(self.CARRY, value > 255)
        self.store_byte(addr, self.set_nz(value & 0xFF))

    def BRK(self, d):
        self.stack_push_word((self.pc + 1) & 0xFFFF)
        self.set_flag(self.BREAK, True)
        self.PHP(0)
        self.SEI(0)
        self.pc = self.get_word(0xFFFE)  # IRQ

    def JMP(self, addr): self.pc = addr - 2

    def JSR(self, addr):
        if addr == 0xE7B7 and self.pc > 0xC000: # samo i jedino ako rutinu poziva ROM
            if not self.tape_out:
                self.tape_out = wave.open(self.get_filename(), 'w')
                self.tape_out.setparams((1, 1, 44100, 0, 'NONE', 'not compressed'))
            self.tape_out.writeframes(chr(255 * self.flipflop) * (1 + (self.y > 15)) * 10)

        self.stack_push_word((self.pc + 1) & 0xFFFF)
        self.pc = addr - 2

    def LSR(self, addr):
        self.set_flag(self.NEGATIVE, False)
        self.set_flag(self.CARRY, self.get_byte(addr) & 1)
        self.store_byte(addr, (self.get_byte(addr) >> 1) & 0x7F)
        self.set_flag(self.ZERO, self.get_byte(addr) == 0)

    def RTI(self, d):
        self.flags = self.stack_pop() | self.BREAK | self.UNUSED
        self.pc = self.stack_pop_word()

    def RTS(self, d):
        self.pc = self.stack_pop_word()
        self.pc = (self.pc + 1) & 0xFFFF

    def ADDITION(self, arg):
        result = (arg & 0XFF) + self.a + self.get_flag(self.CARRY)
        self.set_flag(self.OVERFLOW, (~(arg ^ self.a)) & (self.a ^ result) & 0x80)
        self.set_flag(self.CARRY, result > 255)
        self.a = self.set_nz(result) & 0xFF

    def ADC(self, addr): self.ADDITION(self.get_byte(addr))
    def SBC(self, addr): self.ADDITION(~self.get_byte(addr))

    def COMPARE(self, what, addr):
        self.set_flag(self.CARRY, self.set_nz(what - self.get_byte(addr)) >= 0)

    def CMP(self, addr): self.COMPARE(self.a, addr)
    def CPX(self, addr): self.COMPARE(self.x, addr)
    def CPY(self, addr): self.COMPARE(self.y, addr)

    def BRANCH(self, addr, flag, condition):
        if self.get_flag(flag) is condition:
            self.pc = addr
            self.cycles += 1                            # Ako se grana, to je 1 ekstra ciklus


    def BCS(self, addr): self.BRANCH(addr, self.CARRY, True)
    def BCC(self, addr): self.BRANCH(addr, self.CARRY, False)
    def BEQ(self, addr): self.BRANCH(addr, self.ZERO, True)
    def BNE(self, addr): self.BRANCH(addr, self.ZERO, False)
    def BMI(self, addr): self.BRANCH(addr, self.NEGATIVE, True)
    def BPL(self, addr): self.BRANCH(addr, self.NEGATIVE, False)
    def BVS(self, addr): self.BRANCH(addr, self.OVERFLOW, True)
    def BVC(self, addr): self.BRANCH(addr, self.OVERFLOW, False)

    def step(self):
        opcode = self.memory[self.pc]
        self.pc = self.pc + 1 & 0xFFFF
        instruction, addressing, cycles = self._opcodes[opcode]
        instruction(addressing())
        self.pc += self.ticks[addressing]
        self.cycles += cycles


cpu = CPU(bytearray([0xFF]*0xC000) + bytearray(open('ORAO13.ROM', 'rb').read()))
pygame.mixer.pre_init(44100, 8, 1, buffer=2048)
pygame.init()
ratio, cpu.channel, running = 0, pygame.mixer.Channel(0), True
pygame.time.set_timer(pygame.USEREVENT + 1, 40)

while running:
    before, previous_loop_cycles = datetime.datetime.now(), cpu.cycles
    time_elapsed = lambda: (datetime.datetime.now()-before).microseconds + 1

    for i in range(5000):
        cpu.step()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 650 < x < 700 and 720 < y < 790:             # Reset button
                cpu.__init__(cpu.memory[:])                 # Warm reset

        if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            for address, keycodes in cpu._kbd.iteritems():
                keys = map(pygame.key.get_pressed().__getitem__, keycodes)
                cpu.memory[address] = ~numpy.dot(keys, [16,32,64,128][:len(keys)]) & 0xFF

        if event.type == pygame.USEREVENT + 1:
            cpu.screen.blit(cpu.background, [0, 0])
            cpu.screen.blit(pygame.transform.smoothscale(cpu.terminal, (512, 512)), [150, 140])

            pygame.display.set_caption('({0:.2f} MHz) Orao Emulator v0.1'.format(ratio))
            pygame.display.update()

            cpu.tape_out = None if cpu.cycles - cpu.last_sound_cycles > 20000 else cpu.tape_out

            if len(cpu.sndbuf) > 4096 or cpu.sndbuf and cpu.cycles - cpu.last_sound_cycles > 20000:
                while cpu.channel.get_queue():
                    if time_elapsed() > 10000: break

                cpu.channel.queue(pygame.sndarray.make_sound(numpy.uint8(cpu.sndbuf)))
                cpu.sndbuf = []

    overshoot = cpu.cycles - previous_loop_cycles - time_elapsed()
    pygame.time.wait((overshoot > 0) * overshoot // 1000)      # Pričekaj da budemo cycle exact

    ratio = 1.0 * (cpu.cycles - previous_loop_cycles) / time_elapsed()

pygame.quit()
