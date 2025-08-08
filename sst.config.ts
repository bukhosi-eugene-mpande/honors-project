import { SSTConfig } from "sst";

export default {
  config(_input) {
    return {
      name: "honors-project",
      region: "us-east-1",
    };
  },
  async stacks(app) {
    const { API } = await import("./stacks/MyStack");
    app.stack(API);
  }
};
