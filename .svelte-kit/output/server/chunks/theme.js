import { R as writable } from "./index-server.js";
import "./index-server2.js";
function createTheme() {
	const { subscribe, set, update } = writable("dark");
	return {
		subscribe,
		init() {},
		toggle() {
			update((mode) => {
				return mode === "dark" ? "light" : "dark";
			});
		}
	};
}
var theme = createTheme();
//#endregion
export { theme as t };
