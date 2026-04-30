import time
import numpy as np
import pygame  # python3 -m pip install -U pygame==2.6.0

from src.util.dft_loader import load_spectra_from_file


class Visualizer:

    def __init__(self, win_w=800, win_h=600):
        # pygame inits
        pygame.init()
        pygame.mixer.init()
        pygame.font.init()

        # window
        self.win_w = None
        self.win_h = None
        self.screen = None
        self.vis_w = None
        self.vis_h = None
        self.horiz_shift = 80
        self.vert_shift = 60
        self.set_window_size(win_w, win_h, win_w - self.horiz_shift * 2, win_h - self.vert_shift * 2)

        pygame.display.set_caption("Audio Spectrum Visualizer")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Trebuchet MS", 18)

        ## visual settings
        self.n_bars = 128

        #background color
        self.bg_surface = None
        self.bg_color = (0, 0, 0)
        self.bg_mode = "color"

        # bar color
        self.bar_color = (255, 255, 255)
        self.bar_grad = None
        self.bar_mode = "color"

        # font color
        self.font_color = (255, 255, 255)

        ## audio adjustments
        self.dynamic_range = 90
        self.gain = 0.75

    def set_window_size(self, w=None, h=None, vis_w=None, vis_h=None, horiz_shift=None, vert_shift=None):
        # TODO this is broken, and I dont want to try to figure out why...
        if w is not None:
            self.win_w = w
        if h is not None:
            self.win_h = h
        if vis_w is not None:
            self.vis_w = vis_w
        if vis_h is not None:
            self.vis_h = vis_h
        if horiz_shift is not None:
            self.horiz_shift = horiz_shift
        if vert_shift is not None:
            self.vert_shift = vert_shift
        self.screen = pygame.display.set_mode((w, h))

    def set_dynamic_range(self, db):
        self.dynamic_range = db

    def set_gain(self, gain):
        self.gain = gain

    def set_n_bars(self, n_bars):
        self.n_bars = n_bars

    def set_font_color(self, color: tuple[int, int, int] = (255, 255, 255)):
        self.font_color = color

    def set_font_size(self, size: int = 20):
        self.font = pygame.font.SysFont("Trebuchet MS", size)

    def set_background_color(self, mode="color", data=(0, 0, 0)):
        """
        :param mode: "color", "image", or "gradient"
        :param data:
                - RGB tuple (color)
                - file path string (image)
                - tuple of two RGB tuples (gradient)
        """
        self.bg_mode = mode

        if mode == "color":
            self.bg_color = data

        elif mode == "image":
            # Load the image and scale it to fit the window exactly
            img = pygame.image.load(data).convert()
            self.bg_surface = pygame.transform.scale(img, (self.win_w, self.win_h))

        elif mode == "gradient":
            color_top, color_bottom = data
            # make a 2x2 surface, draw top/bottom, and stretch it
            tiny_surf = pygame.Surface((2, 2))
            pygame.draw.line(tiny_surf, color_top, (0, 0), (1, 0))
            pygame.draw.line(tiny_surf, color_bottom, (0, 1), (1, 1))

            # smoothscale blends the colors seamlessly
            self.bg_surface = pygame.transform.smoothscale(tiny_surf, (self.win_w, self.win_h))

    def set_bar_color(self, mode="color", data=(255, 255, 255)):
        """
        :param mode: "color", or "gradient"
        :param data:
                - RGB tuple (color)
                - tuple of two RGB tuples (gradient)
        """
        self.bar_mode = mode

        if mode == "color":
            self.bar_color = data

        elif mode == "gradient":
            self.bar_grad = []
            start = data[0]
            end = data[1]

            for i in range(self.n_bars):
                r = int(start[0] + i / (self.n_bars - 1) * (end[0] - start[0]))
                g = int(start[1] + i / (self.n_bars - 1) * (end[1] - start[1]))
                b = int(start[2] + i / (self.n_bars - 1) * (end[2] - start[2]))

                self.bar_grad.append((r, g, b))


    def visualize_from_file(self, spec_path, wav_path, fps=30):
        # load from existing custom file
        spectra, fs = load_spectra_from_file(spec_path)

        ### x axis mapping ###
        bar_w = self.vis_w / self.n_bars

        n_fft_bins = spectra.shape[1]
        chuck_size = int(n_fft_bins - 1) * 2

        # get the actual frequencies from the FFT (0 - pi)
        freqs = np.fft.rfftfreq(chuck_size, 1 / fs)

        # scale frequencies to logarithmic scale (20Hz - 20kHz)
        log_bins = np.geomspace(20, 20_000, self.n_bars + 1)

        # create a map of where a bar should be based on the logarithmic frequency
        # ex. Bar 1: 20Hz, Bar 2: 40Hz, Bar 3: 80Hz, etc...
        bar_map = []
        for i in range(self.n_bars):
            bar_map.append(
                np.where((freqs >= log_bins[i]) & (freqs < log_bins[i + 1]))[0]
            )

        ### Run ###
        pygame.mixer.music.load(wav_path)
        pygame.mixer.music.play()

        start = time.time()

        ### Main Loop: iterate until spectra file ends ###
        while True:

            # user closed window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            elapsed = time.time() - start
            frame_i = int(elapsed * fps)

            # music is over
            if frame_i >= len(spectra):
                pygame.mixer.music.stop()
                break

            # set the background color
            if self.bg_mode == "color":
                self.screen.fill(self.bg_color)
            else:
                self.screen.blit(self.bg_surface, (0, 0))

            # lower frequencies need to be interpolated since we are using logarithmic scale
            cur_frame = spectra[frame_i]
            interp_frame = np.interp(log_bins, freqs, cur_frame)

            for i in range(self.n_bars):
                magnitude = interp_frame[i]

                # y-axis scaling: 20 * log10(magnitude)
                db = 20 * np.log10(magnitude + 1e-9)
                y = (db + self.dynamic_range) / self.dynamic_range * self.vis_h * self.gain
                y = np.clip(y, 0, self.vis_h)

                # place bar on screen
                pygame.draw.rect(
                    self.screen,
                    self.bar_color if self.bar_mode == "color" else self.bar_grad[i],
                    (
                         int(i * bar_w) + self.horiz_shift,
                         int(self.vis_h - y) + self.vert_shift,
                         int(bar_w),
                         int(y)
                     )
                 )
            self._draw_text()

            pygame.display.flip()
            self.clock.tick(fps)

    def _draw_text(self):
        n_xlabels = 9
        n_ylabels = 6
        x_dist = 4  # vertical distance of x labels from the bottom of the visual
        y_dist = 35  # horizontal distance of y labels from the left of the visual
        y_vert_correction = -25
        dx = self.vis_w / n_xlabels
        dy = self.vis_h / n_ylabels

        # x axis labels
        for i, f in zip(range(n_xlabels), np.geomspace(20, 20_000, n_xlabels + 1)):
            # truncate the right side of the number for a clearner look
            txt = f
            if f < 100:
                txt = f"{f // 10 * 10:.0f}"
            else: #f < 1000:
                txt = f"{f // 100 * 100:.0f}"

            # draw to screen
            self.screen.blit(
                self.font.render(
                    txt, True, self.font_color
                ),
                (self.horiz_shift + dx * i, self.vis_h + self.vert_shift + x_dist)
            )

        # frequency label
        x_label_txt = self.font.render("Frequency (Hz)", True, self.font_color)
        self.screen.blit(
            x_label_txt,
            ( self.win_w // 2 - x_label_txt.get_width() // 2, self.vis_h + self.vert_shift + 7 * x_dist)
        )

        # y axis labels
        for i, db in zip(range(n_ylabels + 1), np.linspace(self.dynamic_range, 0, n_ylabels + 1)):
            txt = f"-{db:.0f}"
            self.screen.blit(
                self.font.render(
                    txt, True, self.font_color
                ),
                (self.horiz_shift - y_dist, (self.vis_h + self.vert_shift) - dy * i + y_vert_correction)
            )

        # amplitude label
        y_label_txt = self.font.render("Amplitude (dB)", True, self.font_color)
        y_label_txt = pygame.transform.rotate(y_label_txt, 90)
        self.screen.blit(
            y_label_txt,
            (self.horiz_shift - y_dist * 2, self.win_h // 2 - y_label_txt.get_height() // 2)
        )
