import { GlobalStore } from "./global";
import { HistoryStore } from "./history";

export default {
  global: () => GlobalStore(),
  history: () => HistoryStore(),
};
