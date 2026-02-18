import type { ReactNode } from "react";

const icon = (paths: ReactNode, filled = false) => (
  <svg
    className={filled ? "command-icon command-icon--filled" : "command-icon"}
    viewBox="0 0 24 24"
    aria-hidden="true"
  >
    {paths}
  </svg>
);

export const getCommandIcon = (button: string) => {
  switch (button) {
    case "power_toggle":
    case "power_on":
    case "power_off":
      return icon(
        <>
          <circle cx="12" cy="12" r="8" />
          <path d="M12 4v6" />
        </>
      );
    case "volume_up":
      return icon(
        <>
          <path d="M5 10h4l5-4v12l-5-4H5z" />
          <path d="M17 9c1 1 1 5 0 6" />
          <path d="M19 7c2 2 2 8 0 10" />
        </>
      );
    case "volume_down":
      return icon(
        <>
          <path d="M5 10h4l5-4v12l-5-4H5z" />
          <path d="M18 12h-3" />
        </>
      );
    case "mute":
      return icon(
        <>
          <path d="M5 10h4l5-4v12l-5-4H5z" />
          <path d="M17 9l4 6" />
          <path d="M21 9l-4 6" />
        </>
      );
    case "direction_up":
      return icon(<path d="M12 6l-5 6h10z" />);
    case "direction_down":
      return icon(<path d="M12 18l5-6H7z" />);
    case "direction_left":
      return icon(<path d="M6 12l6-5v10z" />);
    case "direction_right":
      return icon(<path d="M18 12l-6 5V7z" />);
    case "select":
      return icon(<circle cx="12" cy="12" r="4" />);
    case "back":
      return icon(<path d="M15 6l-6 6 6 6" />);
    case "menu":
      return icon(
        <>
          <path d="M5 7h14" />
          <path d="M5 12h14" />
          <path d="M5 17h14" />
        </>
      );
    case "exit":
      return icon(
        <>
          <path d="M9 5h6a2 2 0 0 1 2 2v4" />
          <path d="M15 19H9a2 2 0 0 1-2-2v-4" />
          <path d="M13 12H4" />
          <path d="M7 9l-3 3 3 3" />
        </>
      );
    case "guide":
      return icon(
        <>
          <circle cx="12" cy="12" r="8" />
          <path d="M12 8v8" />
          <path d="M8 12h8" />
        </>
      );
    case "play":
    case "playpause":
      return icon(<path d="M8 6l10 6-10 6z" />);
    case "pause":
      return icon(
        <>
          <path d="M8 6h3v12H8z" />
          <path d="M13 6h3v12h-3z" />
        </>
      );
    case "stop":
      return icon(<rect x="7" y="7" width="10" height="10" />);
    case "fast_forward":
      return icon(
        <>
          <path d="M4 6l7 6-7 6z" />
          <path d="M12 6l7 6-7 6z" />
        </>
      );
    case "rewind":
      return icon(
        <>
          <path d="M20 6l-7 6 7 6z" />
          <path d="M12 6l-7 6 7 6z" />
        </>
      );
    case "next_track":
      return icon(
        <>
          <path d="M6 6l8 6-8 6z" />
          <path d="M16 6v12" />
        </>
      );
    case "previous_track":
      return icon(
        <>
          <path d="M18 6l-8 6 8 6z" />
          <path d="M8 6v12" />
        </>
      );
    case "record":
      return icon(<circle cx="12" cy="12" r="5" />, true);
    case "channel_up":
      return icon(
        <>
          <path d="M12 6l5 6H7z" />
          <path d="M7 16h10" />
        </>
      );
    case "channel_down":
      return icon(
        <>
          <path d="M12 18l-5-6h10z" />
          <path d="M7 8h10" />
        </>
      );
    case "green":
      return <span className="command-icon command-icon--color command-icon--green" />;
    case "red":
      return <span className="command-icon command-icon--color command-icon--red" />;
    case "blue":
      return <span className="command-icon command-icon--color command-icon--blue" />;
    case "yellow":
      return <span className="command-icon command-icon--color command-icon--yellow" />;
    case "number_zero":
      return <span className="command-icon__text">0</span>;
    case "number_one":
      return <span className="command-icon__text">1</span>;
    case "number_two":
      return <span className="command-icon__text">2</span>;
    case "number_three":
      return <span className="command-icon__text">3</span>;
    case "number_four":
      return <span className="command-icon__text">4</span>;
    case "number_five":
      return <span className="command-icon__text">5</span>;
    case "number_six":
      return <span className="command-icon__text">6</span>;
    case "number_seven":
      return <span className="command-icon__text">7</span>;
    case "number_eight":
      return <span className="command-icon__text">8</span>;
    case "number_nine":
      return <span className="command-icon__text">9</span>;
    case "brightness_up":
      return icon(
        <>
          <circle cx="12" cy="12" r="4" />
          <path d="M12 3v3" />
          <path d="M12 18v3" />
          <path d="M3 12h3" />
          <path d="M18 12h3" />
        </>
      );
    case "brightness_down":
      return icon(
        <>
          <circle cx="12" cy="12" r="4" />
          <path d="M8 12h8" />
        </>
      );
    case "turn_on":
      return icon(<path d="M6 12l4 4 8-8" />);
    case "turn_off":
      return icon(
        <>
          <path d="M8 8l8 8" />
          <path d="M16 8l-8 8" />
        </>
      );
    default:
      return icon(
        <>
          <circle cx="12" cy="12" r="2" />
          <circle cx="6" cy="12" r="2" />
          <circle cx="18" cy="12" r="2" />
        </>
      );
  }
};
