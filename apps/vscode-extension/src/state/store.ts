export class StateStore {
    private static _infraSummary: any = null;

    public static setInfraSummary(summary: any) {
        this._infraSummary = summary;
    }

    public static getInfraSummary() {
        return this._infraSummary;
    }
}
